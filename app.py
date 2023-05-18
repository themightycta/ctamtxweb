from flask import Flask, request, render_template, send_file, after_this_request
import struct
from PIL import Image
import io, os
import tempfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image():
    # Get the input image file from the request
    input_image = request.files['image']

    # Convert image to PIL Image object
    image = Image.open(input_image)
    image = image.convert("RGB")

    # Create output file path
    output_mtx_path = os.path.splitext(input_image.filename)[0] + ".mtx"

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

    # Create a file-like object from the saved file
    with open(output_mtx_path, 'rb') as file:
        file_like = io.BytesIO(file.read())

    # Delete the file after returning it
    @after_this_request
    def delete_output_file(response):
        os.remove(output_mtx_path)
        return response

    return send_file(file_like, mimetype='application/octet-stream', download_name=output_mtx_path)

@app.route("/")
def myroute():
    return render_template("index.html")

if __name__ == "__main__":
	app.run()
