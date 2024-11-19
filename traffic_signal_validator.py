"""Validate a solution for a Traffic Signaling Instance of Prishtina.

In order to validate the solution instance you need to provide the input instance
and the output instance paths.

Example usage:
    python traffic_signal_validator.py --input_instance input_instance.json --output_instance solution.json

Aliases:
    -i, --input_instance
    -o, --output_instance
"""
import argparse
import json


def load_json(json_path: str) -> dict:
    with open(json_path, 'r') as file:
        return json.load(file)


def are_phase_orders_valid(input_data: dict, output_data: dict) -> bool:
    def check_contiguous_order(first_list: list[str], second_list: list[str]) -> bool:
        try:
            start_index = first_list.index(second_list[0])
        except ValueError:
            return False

        for i in range(1, len(second_list)):
            if start_index + i >= len(first_list) or first_list[start_index + i] != second_list[i]:
                return False

        return True

    input_constraints = input_data['constraints']
    output_intersections = output_data['intersections']

    phase_constraints_by_intersection = {
        constraint['intersection_name']: constraint['streets']
        for constraint in input_constraints
        if constraint['type'] == 'signal_phase_order'
    }

    phase_order_correct = True

    for intersection in output_intersections:
        if len(intersection['phases']) > 1 and intersection['intersection_name'] in phase_constraints_by_intersection:
            street_representatives = [
                list(phase['streets'][0].keys())[0]
                for phase in intersection['phases']
            ]
            phase_orders = phase_constraints_by_intersection[intersection['intersection_name']]
            phase_order_correct = check_contiguous_order(street_representatives, phase_orders)
            if not phase_order_correct:
                print(f'Wrong phase order for {intersection["intersection_name"]}')

    return phase_order_correct


def are_nr_phases_valid(input_data: dict, output_data: dict) -> bool:
    input_constraints = input_data['constraints']
    output_intersections = output_data['intersections']

    constraints_by_intersection = {}

    for constraint in input_constraints:
        if constraint['type'] == 'simultaneously_signal':
            intersection_name = constraint['intersection_name']
            constraints_by_intersection.setdefault(intersection_name, 0)
            constraints_by_intersection[intersection_name] += 1

    phase_error = True

    for intersection in output_intersections:
        intersection_name = intersection['intersection_name']
        phases_count = len(intersection['phases'])
        constraints_count = constraints_by_intersection.get(intersection_name, 0)
        if phases_count != constraints_count:
            print(f'Wrong number of phases for {intersection_name} intersection. '
                  f'It should have {constraints_count} phases and it has {phases_count}.')
            phase_error = False

    return phase_error


def are_cycle_lengths_valid(input_data: dict, output_data: dict) -> bool:
    limit_on_minimum_cycle_length = input_data['simulation']['limit_on_minimum_cycle_length']
    limit_on_maximum_cycle_length = input_data['simulation']['limit_on_maximum_cycle_length']

    output_intersections = output_data['intersections']

    cycle_limit_error = True

    for intersection in output_intersections:
        if len(intersection['phases']) > 1:
            street_representatives = [
                list(phase['streets'][0].values())[0]
                for phase in intersection['phases']
            ]

            all_red_phase_interval = intersection['all_red_phase_interval']
            pedestrian_phase_interval = intersection['pedestrian_phase_interval']
            total_intersection_time = sum(street_representatives) + pedestrian_phase_interval + all_red_phase_interval

            if total_intersection_time > limit_on_maximum_cycle_length:
                print(f'The cycle time has exceeded the maximum allowed. '
                      f'Intersection name: {intersection["intersection_name"]}. '
                      f'Total time: {total_intersection_time}')
                cycle_limit_error = False

            if total_intersection_time < limit_on_minimum_cycle_length:
                print(f'The cycle time has exceeded the minimum allowed. '
                      f'Intersection name: {intersection["intersection_name"]}. '
                      f'Total time: {total_intersection_time}')
                cycle_limit_error = False

    return cycle_limit_error


def are_green_time_durations_valid(input_data: dict, output_data: dict) -> bool:
    limit_on_minimum_green_phase_duration = input_data['simulation']['limit_on_minimum_green_phase_duration']
    limit_on_maximum_green_phase_duration = input_data['simulation']['limit_on_maximum_green_phase_duration']

    output_intersections = output_data['intersections']

    green_time_duration_error = True

    for intersection in output_intersections:
        if len(intersection['phases']) >= 1:
            street_representatives = [
                list(phase['streets'][0].values())[0]
                for phase in intersection['phases']
            ]
            for duration in street_representatives:
                if duration < limit_on_minimum_green_phase_duration:
                    print(f'The green time has exceeded the minimum allowed. '
                          f'Intersection name: {intersection["intersection_name"]}. '
                          f'Green time: {duration}')
                    green_time_duration_error = False

            for duration in street_representatives:
                if duration > limit_on_maximum_green_phase_duration:
                    print(f'The green time has exceeded the maximum allowed. '
                          f'Intersection name: {intersection["intersection_name"]}. '
                          f'Green time: {duration}')
                    green_time_duration_error = False

    return green_time_duration_error


def are_street_representatives_valid(input_data: dict, output_data: dict) -> bool:
    input_constraints = input_data['constraints']
    output_intersections = output_data['intersections']

    constraints_by_intersection = {}

    for constraint in input_constraints:
        if constraint['type'] == 'simultaneously_signal':
            intersection_name = constraint['intersection_name']
            constraints_by_intersection.setdefault(intersection_name, [])
            constraints_by_intersection[intersection_name].append(constraint['streets'][0])

    street_representative_error = True

    for intersection in output_intersections:
        if len(intersection['phases']) > 1:
            street_representatives = [
                list(phase['streets'][0].keys())[0]
                for phase in intersection['phases']
            ]
            if intersection['intersection_name'] not in constraints_by_intersection:
                continue

            input_representatives = constraints_by_intersection[intersection['intersection_name']]
            street_representatives = sorted(street_representatives)
            input_representatives = sorted(input_representatives)
            if street_representatives != input_representatives:
                print(f'Street representative error in intersection: {intersection["intersection_name"]}. \n'
                      f'The street representatives in the solution: {street_representatives}. \n'
                      f'The street representatives in the input instance: {input_representatives}. \n')
                street_representative_error = False

    return street_representative_error


def are_green_times_equal_inside_the_same_phase(output_data: dict) -> bool:
    output_intersections = output_data['intersections']

    same_green_time_error = True

    for intersection in output_intersections:
        for phase in intersection['phases']:
            phase_green_times = []
            for elem in phase['streets']:
                phase_green_times.append(list(elem.values())[0])

            if not all(x == phase_green_times[0] for x in phase_green_times):
                print(f'The green time is not the same in the following intersection: '
                      f'{intersection["intersection_name"]}. The values of phase green time: {phase_green_times}')
                same_green_time_error = False

    return same_green_time_error


def main(input_instance: str, output_instance: str) -> None:
    input_data = load_json(input_instance)
    output_data = load_json(output_instance)

    is_solution_valid = True

    if not are_street_representatives_valid(input_data, output_data):
        is_solution_valid = False
        print()

    if not are_nr_phases_valid(input_data, output_data):
        is_solution_valid = False
        print()

    if not are_phase_orders_valid(input_data, output_data):
        is_solution_valid = False
        print()

    if not are_cycle_lengths_valid(input_data, output_data):
        is_solution_valid = False
        print()

    if not are_green_time_durations_valid(input_data, output_data):
        is_solution_valid = False
        print()

    if not are_green_times_equal_inside_the_same_phase(output_data):
        is_solution_valid = False
        print()

    if is_solution_valid:
        print('\nOutput is valid.')
    else:
        print('\nOutput is not valid.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_instance', type=str, required=True)
    parser.add_argument('-o', '--output_instance', type=str, required=True)

    args = parser.parse_args()
    main(args.input_instance, args.output_instance)
