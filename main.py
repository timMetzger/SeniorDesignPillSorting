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
                      "first_name": 'Jane',
                      "last_name": "Doe",
                      "age": "65",
                      "address": "12 Seuss Valley MO",
                      "prescription": {"Benadryl": 2, "Motrin": 6},
                      "frequency": [2, 2],
                      "days_of_week": [[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1]]
                      },{"id": "1",
                      "first_name": 'Test1',
                      "last_name": "Test1",
                      "age": "999",
                      "address": "Test1",
                      "prescription": {"Aspirin": 2},
                      "frequency": [1],
                      "days_of_week": [[1, 0, 1, 0, 0, 0, 0]]
                      },{"id": "2",
                      "first_name": 'Test2',
                      "last_name": "Test2",
                      "age": "999",
                      "address": "Test2",
                      "prescription": {"Benadryl": 2, "Motrin": 6},
                      "frequency": [2, 2],
                      "days_of_week": [[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1]]
                      },{"id": "3",
                      "first_name": 'Test3',
                      "last_name": "Test3",
                      "age": "999",
                      "address": "Test3",
                      "prescription": {"Benadryl": 2, "Motrin": 6,"Aspirin": 2, "Advil": 6,"Tylenol": 2, "Claritin": 6},
                      "frequency": [2, 2, 2, 2, 2, 2],
                      "days_of_week": [[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1],[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1],[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1]]
                      },{"id": "4",
                      "first_name": 'Test4',
                      "last_name": "Test4",
                      "age": "999",
                      "address": "Test4",
                      "prescription": {"Benadryl": 2, "Motrin": 6,"Aspirin": 2, "Advil": 6,"Tylenol": 2, "Claritin": 6},
                      "frequency": [2, 2, 2, 2, 2, 2],
                      "days_of_week": [[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1],[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1],[1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1]]
                      }]
    Pill_Sorting_Interface(user_info)


if __name__ == "__main__":
    main()
