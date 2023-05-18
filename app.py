from flask import Flask, request, render_template
import struct
from PIL import Image
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image():
    # Get the input image file from the request
    input_image = request.files['image']

    # Convert image to PIL Image object
    image = Image.open(input_image)
    image = image.convert("RGB")

    # Create output file path
    output_mtx_path = 'output.mtx'

    # Write image data to MTXv0 file
    with open(output_mtx_path, 'wb') as output_file:
        # Write header (MTXv0 identifier)
        output_file.write(struct.pack('<I', 0x3058544D))

        # Write image data chunks
        image_width, image_height = image.size
        for _ in range(2):
            # Calculate chunk size
            chunk_size = image_width * image_height * 3 + 8

            # Write chunk size
            output_file.write(struct.pack('<I', chunk_size))

            # Save image to temporary JPEG file
            temp_jpeg = io.BytesIO()
            image.save(temp_jpeg, format='JPEG', quality=90)

            # Read JPEG data from temporary file
            temp_jpeg.seek(0)
            jpeg_data = temp_jpeg.read()

            # Write JPEG data
            output_file.write(jpeg_data)

            # Double the size of the image for the second chunk
            image_width *= 2
            image_height *= 2

    return f"Image converted to MTXv0 format: {output_mtx_path}"

@app.route("/")
def myroute():
	return render_template("index.html")

if __name__ == '__main__':
    app.run()
