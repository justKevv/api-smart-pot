from flask import request, jsonify, send_file
from model import Model
from cloudinary_handler import CloudinaryHandler
import io
import requests
from werkzeug.exceptions import BadRequest # Import BadRequest

class Controller:
    def __init__(self, app_instance):
        self._app = app_instance
        self.__db_model = Model()
        self.__cloudinary = CloudinaryHandler()

        self.__setup_routes()

    def __setup_routes(self):
        self._app.add_url_rule('/insert/user', view_func=self._insert_user, methods=['POST'])
        self._app.add_url_rule('/post/image/<id>', view_func=self._post_image, methods=['POST'])
        self._app.add_url_rule('/get/image/<id>', view_func=self._get_image, methods=['GET'])
        self._app.add_url_rule('/insert/data/<id>', view_func=self._insert_data, methods=['POST'])
        self._app.add_url_rule('/find/data/<id>', view_func=self._find_data, methods=['GET'])
        self._app.add_url_rule('/find/user/<id>', view_func=self._find_pot_ids, methods=['GET'])

    def _insert_user(self):
        try:
            data = request.get_json()
            chat_id = data.get('chat_id')
            pot_id = data.get('pot_id')
            self.__db_model.insert_user(chat_id, pot_id)
            url = self.__cloudinary.upload_image('white.jpg', public_id=str(pot_id))
            self.__db_model.insert_image(pot_id, url)

            return jsonify({'message': 'User saved successfully'}), 201
        except Exception as e:
            return str(e), 500

    def _post_image(self, id):
        try:
            id = int(id)
            if self.__db_model.is_user(id):
                image_bytes = request.data
                url = self.__cloudinary.upload_image(image_bytes, public_id=str(id))
                return jsonify({'message': 'Image processed and uploaded successfully!', 'url': url}), 200
            else:
                return jsonify({'message': 'User not found.'}), 404
        except Exception as e:
            return str(e), 500

    def _get_image(self, id):
        try:
            id = int(id)
            if self.__db_model.is_user(id):
                image_url = self.__db_model.find_image(id)
                response = requests.get(image_url)
                if response.status_code == 200:
                    return send_file(io.BytesIO(response.content), mimetype='image/jpeg')
                else:
                    return jsonify({'message': 'Image not found.'}), 404
            else:
                return jsonify({'message': f'User not found.'}), 404
        except Exception as e:
            return str(e), 500


    def _insert_data(self, id):
        try:
            # 1. Validate pot ID format
            try:
                pot_id = int(id)
            except ValueError:
                return jsonify({'message': f'Invalid pot ID format: "{id}". Must be an integer.'}), 400

            # 2. Check if user/pot exists (using the corrected is_user)
            if not self.__db_model.is_user(pot_id):
                 return jsonify({'message': f'Pot ID {pot_id} not associated with any user.'}), 404

            # 3. Parse JSON and handle parsing errors explicitly
            try:
                data = request.get_json()
                if data is None:
                    # This happens if Content-Type is not application/json or body is empty/invalid
                    return jsonify({'message': 'Invalid JSON payload or missing/incorrect Content-Type header (must be application/json).'}), 400
            except BadRequest as e:
                # Catches errors during JSON parsing (e.g., malformed JSON)
                return jsonify({'message': f'Failed to decode JSON object: {e.description}'}), 400

            # 4. Check for required keys in the parsed JSON
            ph = data.get('ph')
            soil = data.get('soil')

            if ph is None or soil is None:
                 return jsonify({'message': 'Missing required key(s) in JSON payload. Both "ph" and "soil" must be provided.'}), 400

            # Optional: Add type validation if needed (e.g., ensure ph is a number, soil is an integer)
            # try:
            #     ph_val = float(ph)
            #     soil_val = int(soil)
            # except (ValueError, TypeError):
            #     return jsonify({'message': '"ph" must be a number and "soil" must be an integer.'}), 400

            # 5. Insert data if all checks pass
            self.__db_model.insert_data(pot_id, ph, soil) # Use validated pot_id and data
            return jsonify({'message': 'Data saved successfully'}), 201

        # 6. Catch-all for other unexpected errors (e.g., database issues)
        except Exception as e:
            # Log the actual error on the server for debugging
            print(f"Unexpected error in _insert_data for pot_id {id}: {e}") # Consider using Flask's logger
            return jsonify({'message': 'An internal server error occurred.'}), 500

    def _find_data(self, id):
        try:
            id = int(id)
            if self.__db_model.is_user(id):
                data = self.__db_model.find_data(id)
                return jsonify(data), 200
            else:
                return jsonify({'message': 'User not found.'}), 404
        except Exception as e:
            return str(e), 500

    def _find_pot_ids(self, id):
        try:
            id = int(id)
            data = self.__db_model.get_pot_ids(id)
            return jsonify(data), 200
        except Exception as e:
            return str(e), 500
    def run(self):
        self._app.run(host='0.0.0.0')
