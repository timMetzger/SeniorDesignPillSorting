# By: Timothy Metzger

from Pill_Sorting_Interface import Pill_Sorting_Interface

def main():
    # Hardcoded database
    user_info = [{"id": "1234",
                  "first_name": 'John',
                  "last_name": "Smith",
                  "age": "72",
                  "address": "96 Whooovile RD KT",
                  "prescription": {"Advil": 2, "Motrin": 3},
                  "frequency": [1, 1],
                  "days_of_week": [[1, 0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0]]
                  }, {"id": "1281",
                      "first_name": 'Jan',
                      "last_name": "Doe",
                      "age": "65",
                      "address": "12 Seuss Valley MO",
                      "prescription": {"Benadryl": 2, "Motrin": 6},
                      "frequency": [2, 2],
                      "days_of_week": [[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1]]
                      }]
    Pill_Sorting_Interface(user_info)


if __name__ == "__main__":
    main()
