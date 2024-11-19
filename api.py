import os
import subprocess
import time
from flask import Flask, json, jsonify, request, send_file
from BeeHiveOptimization import BeeHive
import GlobalFunctions as gl
import traceback 

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    timeout = int(request.form.get('timeout', 10))
    
    try:
        # Save the uploaded file to a temporary location
        input_filename = 'input.json'
        output_filename = 'output.json'
        file.save(input_filename)

        output_file_path = os.path.abspath('output/output.json')

        start = time.time()
        total_duration, bonus_points, intersections, streets, name_to_i_street, paths, \
            duration_to_pass_through_a_traffic_light, yellow_phase, limit_on_minimum_cycle_length, \
            limit_on_maximum_cycle_length, limit_on_minimum_green_phase_duration, \
            limit_on_maximum_green_phase_duration, i_id_to_intersection = gl.readInput(input_filename)
        
        print(limit_on_minimum_cycle_length)

        if timeout:
            use_seed = output_file_path
            solution_file_path = './seeds/' + input_filename + '.txt.out'
            print("kendej")
            schedule, score, cars, avg , resultJSON = BeeHive(streets, intersections, paths, total_duration, bonus_points, start,
                                                yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration,
                                                limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                                limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light,
                                                i_id_to_intersection, output_file_path, use_seed, solution_file_path, timeout)
            
            print(resultJSON)
            return resultJSON
        else:
            schedule, score, cars, avg, resultJSON = BeeHive(streets, intersections, paths, total_duration, bonus_points, start,
                                                yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration,
                                                limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                                limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light,
                                                i_id_to_intersection, output_file_path, 10)
            
            print(resultJSON)
            return resultJSON
            

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the temporary files
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)