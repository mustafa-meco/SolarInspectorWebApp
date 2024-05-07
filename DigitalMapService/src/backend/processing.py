

def segment_PV(input_image_path):
    import os
    from ultralytics import YOLO
    from PIL import Image

    model = YOLO('segment_weights.pt')

    # Load the input image
    input_image = Image.open(input_image_path)

    # Run inference and save results
    results = model.predict(source=input_image, save=True, save_txt=True, project="satellite", name="labels")
    results_obj = results[0]
    input_filename = os.path.splitext(os.path.basename(input_image_path))[0]

    # Get the path to the saved labels file
    labels_file_path = os.path.join(results_obj.save_dir, "labels", input_filename + ".txt")

    return labels_file_path



def process_image(image_file_path,label_file_path,lat1,lon1,lat2,lon2):

    import cv2
    import numpy as np
    from scipy.signal import find_peaks
    from PIL import Image
    from scipy import ndimage
    import os


    # Read the image
    image = cv2.imread(image_file_path)
    # Prepare the mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    # Read the segmented labels file and extract coordinates for each polygon
    with open(label_file_path, 'r') as file:
        for line in file:
            data = line.strip().split()[1:]  # Skip the first number (class object)
            coordinates = np.array(data, dtype=float).reshape(-1, 2)
            # Adjust coordinates for image dimensions (assuming they are normalized)
            coordinates *= np.array(image.shape[1::-1])  # width (x) and height (y)
            # Draw each polygon on the mask
            cv2.fillPoly(mask, [coordinates.astype(int)], color=255)

    # Apply the mask to the original image to get the segmented part
    segmented_part = cv2.bitwise_and(image, image, mask=mask)
    # Create a gray image
    gray_image = np.full_like(image, 0, dtype=np.uint8)  # You can adjust the gray level here

    # Invert the mask
    inverted_mask = cv2.bitwise_not(mask)

    # Apply the inverted mask to the gray image
    background = cv2.bitwise_and(gray_image, gray_image, mask=inverted_mask)

    # Merge the segmented part with the gray image
    result = cv2.add(segmented_part, background)
    hist = cv2.calcHist([result], [0], None, [256], [0, 256]).flatten()
    hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)  # Normalize for better visibility

    # Smooth the histogram using a windowed filter
    window_size = 5
    smoothed_hist = np.convolve(hist, np.ones(window_size)/window_size, mode='same')

    # Detect peaks with a minimum distance between them to ensure they are far apart
    peaks, _ = find_peaks(smoothed_hist, distance=5)  # distance can be adjusted based on image characteristics

    # Define thresholds for ignoring peaks near the boundaries
    lower_bound = 3
    upper_bound = 250

    # Filter out peaks too close to 0 or 255
    filtered_peaks = [peak for peak in peaks if lower_bound < peak < upper_bound]

    if len(filtered_peaks) > 1:
        sorted_peaks = sorted(filtered_peaks, key=lambda x: smoothed_hist[x], reverse=True)
        major_peaks = sorted_peaks[:2]
        major_peaks.sort()

        # Find the valley between these two peaks as the minimum point
        valley_index = np.argmin(smoothed_hist[major_peaks[0]:major_peaks[1]]) + major_peaks[0]
    else:
        valley_index = np.median(filtered_peaks)  # Fallback if not enough peaks are found

    # Custom binary transformation
    # Custom binary transformation
    if valley_index < 100:
        _, thresholded_image = cv2.threshold(image, valley_index, 255, cv2.THRESH_BINARY)
    else:
        # Reverse transformation with exception for value 0
        thresholded_image = np.where((image > valley_index) | (image == 0), 0, 255).astype(np.uint8)  # Ensure uint8 type here

    # iterations of dilation and erosion
    # Dilate the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_image = cv2.dilate(thresholded_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Adjust kernel size as needed
    eroded_image = cv2.erode(thresholded_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)) # Adjust kernel size as needed
    dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # Adjust kernel size as needed
    eroded_image = cv2.erode(dilated_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # Adjust kernel size as needed
    dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)
    cv2.imwrite('final_image.jpg', dilated_image)

    blur_radius = 1.0
    threshold = 50
    
    img = Image.open('final_image.jpg').convert('L')
    img = np.asarray(img)
    height, width = img.shape
    print("Image shape:", img.shape)

    # Apply Gaussian filter to smooth the image
    imgf = ndimage.gaussian_filter(img, blur_radius)

    # Apply thresholding to find connected components
    labeled, nr_objects = ndimage.label(imgf > threshold)
    print('number of objects',nr_objects)

    # Calculate GPS deltas per pixel
    lon_per_pixel = (lon2 - lon1) / width
    lat_per_pixel = (lat1 - lat2) / height

    def pixel_to_gps(x, y):
        lon = lon1 + x * lon_per_pixel
        lat = lat1 - y * lat_per_pixel
        return (lat, lon)  # Note the order: latitude first, then longitude



    output_directory = os.path.join('static')

    output_image_filename = os.path.splitext(os.path.basename(input_image_path))[0] + 'bbox.txt'
    output_image_path_bbox = os.path.join(output_directory, output_image_filename)
    output_image_filename = os.path.splitext(os.path.basename(input_image_path))[0] + 'gps.txt'
    output_image_path_gps = os.path.join(output_directory, output_image_filename)
    os.makedirs(os.path.dirname(output_image_path_bbox), exist_ok=True)
    os.makedirs(os.path.dirname(output_image_path_gps), exist_ok=True)


    # Open files to write the bounding box properties and GPS coordinates
    with open(output_image_path_bbox, 'w') as bbox_file, open(output_image_path_gps, 'w') as gps_file:
        # Calculate bounding boxes, centers, widths, and heights for each object
        for i in range(1, nr_objects + 1):
            slice_y, slice_x = ndimage.find_objects(labeled == i)[0]
            x1, x2 = slice_x.start, slice_x.stop
            y1, y2 = slice_y.start, slice_y.stop

            width = x2 - x1
            height = y2 - y1

            if width > height:
                y_middle = (y1 + y2) // 2
                bbox_file.write(f"{x1},{y_middle},{x2},{y_middle}\n")
                gps_start = pixel_to_gps(x1, y_middle)
                gps_end = pixel_to_gps(x2, y_middle)
                gps_file.write(f"{gps_start} ,{gps_end}\n")
            else:
                x_middle = (x1 + x2) // 2
                bbox_file.write(f"{x_middle},{y1},{x_middle},{y2}\n")
                gps_start = pixel_to_gps(x_middle, y1)
                gps_end = pixel_to_gps(x_middle, y2)
                gps_file.write(f" {gps_start} , {gps_end}\n")
    return output_image_path_gps






def waypoints_planning(input_image_path,start_lat,start_long,end_lat,end_long):
   label_file_path= segment_PV(input_image_path)
   output_image_path_gps=process_image(input_image_path,label_file_path,start_lat,start_long,end_lat,end_long)
   return output_image_path_gps



input_image_path='F:\\WebPage\\MicroServices\\SolarInspectorWebAppServices\\DigitalMapService\\src\\upload\\Screenshot (59).png'

# output_image_path_gps=waypoints_planning(input_image_path,24.455653, 32.689708,24.453414, 32.692836)



output_image_path_gps=waypoints_planning(input_image_path,24.455653, 32.689708,24.453414, 32.692836)
print('hellllllo')
print(output_image_path_gps)





