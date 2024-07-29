
class MplTrainingData:
    HEADERS = ['remaining_mpl', 'remaining_abbots', 'feature_finished', 'terrain_type',
               'is_end_farmer_time', 'feature_possible_points', 'feature_mpl_on_street', 'selected']

    def __init__(self, training_data: dict):
        self.data = {'remaining_mpl': int(training_data['remaining_mpl']),
                     'remaining_abbots': int(training_data['remaining_abbots']),
                     'feature_finished': int(training_data['feature_finished']),
                     'terrain_type': int(training_data['terrain_type']),
                     'is_end_farmer_time': int(training_data['is_end_farmer_time']),
                     'feature_possible_points': int(training_data['feature_possible_points']),
                     'feature_mpl_on_street': int(training_data['feature_mpl_on_street']),
                     'selected': None}

    def set_selected(self, selected: int):
        self.data['selected'] = selected

    def get_list(self) -> list:
        return [self.data['remaining_mpl'],
                self.data['remaining_abbots'],
                self.data['feature_finished'],
                self.data['terrain_type'],
                self.data['is_end_farmer_time'],
                self.data['feature_possible_points'],
                self.data['feature_mpl_on_street'],
                self.data['selected']]

    def get_list_without_selected(self) -> list:
        return self.get_list()[0:-1]

    def check_data(self, skip_selected: bool = False):
        for header in self.HEADERS:
            if header == 'selected' and skip_selected:
                continue
            if self.data[header] is None:
                print('Missing data for column {}'.format(header))
        for key, value in self.data.items():
            if key == 'selected' and skip_selected:
                continue
            if key not in self.HEADERS:
                print('unwanted key in data {}'.format(key))
            if not isinstance(value, int):
                print('Wrong type for column {}'.format(key))
        if len(self.get_list()) != len(self.HEADERS):
            print("List does not have the correct number of elements")
        if len(self.data.keys()) != len(self.HEADERS):
            print("Dictionary does not have the correct number of elements")
