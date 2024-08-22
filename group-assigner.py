import random
import json
import os
from collections import defaultdict
import csv

class GroupAssigner:
    # def __init__(self, filename="group_data.json", students_file="students.txt"):
    #     self.students = self.load_students(students_file)
    #     self.pair_count = defaultdict(lambda: defaultdict(int))
    #     self.filename = filename
        
    #     # Load existing data if the file exists
    #     if os.path.exists(self.filename):
    #         self.load_data()

    def __init__(self, filename="group_data.json", students_file="students.txt"):
        self.students = self.load_students(students_file)
        self.pair_count = defaultdict(lambda: defaultdict(int))
        self.filename = filename
        
        # Load existing data if the file exists
        if os.path.exists(self.filename):
            self.load_data()
        else:
            # Initialize pair_count for all students
            for student in self.students:
                self.pair_count[student] = defaultdict(int)

    def load_students(self, students_file):
        with open(students_file, 'r') as file:
            students = [line.strip() for line in file.readlines()]
        return students

    def form_groups(self, group_size):
        if group_size > len(self.students):
            raise ValueError("Group size cannot be larger than the number of students.")
        
        ungrouped_students = set(self.students)  # Track students who haven't been grouped yet
        groups = []
        
        while ungrouped_students:
            # Pick the first ungrouped student
            current_student = ungrouped_students.pop()
            
            # Calculate the pair counts with all other ungrouped students
            potential_partners = [(other_student, self.pair_count[current_student].get(other_student, 0))
                                for other_student in ungrouped_students]
            
            # Sort potential partners by the pair count (ascending) to prioritize those they've worked with the least
            potential_partners.sort(key=lambda x: x[1])
            
            # Select the lowest N-1 students to form a group
            selected_students = [student for student, _ in potential_partners[:group_size-1]]
            
            # Add the current student to the selected group
            group = [current_student] + selected_students
            groups.append(group)
            
            # Remove selected students from ungrouped students
            for student in selected_students:
                ungrouped_students.remove(student)
            
            # Track pair counts for the formed group
            for i, student in enumerate(group):
                for j in range(i + 1, len(group)):
                    other_student = group[j]
                    if student != other_student:  # Ensure a student is not paired with themselves
                        self.pair_count[student][other_student] += 1
                        self.pair_count[other_student][student] += 1  # Ensure both directions are counted equally
        
        # Save the new groups to disk
        self.save_data(groups)
        
        return groups



    def get_pair_count(self, student1, student2):
        return self.pair_count[student1][student2]

    def print_pair_counts(self):
        for student, partners in self.pair_count.items():
            for partner, count in partners.items():
                print(f"{student} has worked with {partner} {count} times.")

    # def save_data(self, new_groups):
    #     # Append new groups to existing data
    #     if os.path.exists(self.filename):
    #         with open(self.filename, "r") as file:
    #             data = json.load(file)
    #     else:
    #         data = {"groups": [], "pair_count": {}}

    #     # Append the new group to the sequence of group runs
    #     data["groups"].append(new_groups)
        
    #     # Update pair counts in the file
    #     for student, partners in self.pair_count.items():
    #         if student not in data["pair_count"]:
    #             data["pair_count"][student] = {}
    #         for partner, count in partners.items():
    #             if partner in data["pair_count"][student]:
    #                 data["pair_count"][student][partner] += count
    #             else:
    #                 data["pair_count"][student][partner] = count

    #     # Save updated data back to the file
    #     with open(self.filename, "w") as file:
    #         json.dump(data, file, indent=4)

    def save_data(self, new_groups):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                data = json.load(file)
        else:
            data = {"groups": [], "pair_count": {}}

        data["groups"].append(new_groups)
        
        # Replace the pair counts instead of adding to them
        data["pair_count"] = {student: dict(partners) for student, partners in self.pair_count.items()}

        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)



    # def load_data(self):
    #     with open(self.filename, "r") as file:
    #         data = json.load(file)
            
    #         # Initialize pair_count with defaultdicts
    #         for student, partners in data["pair_count"].items():
    #             self.pair_count[student] = defaultdict(int, partners)

    def load_data(self):
        with open(self.filename, "r") as file:
            data = json.load(file)
            
            # Reset pair_count before loading
            self.pair_count = defaultdict(lambda: defaultdict(int))
            
            # Load the pair counts
            for student, partners in data["pair_count"].items():
                self.pair_count[student].update(partners)

    def generate_pair_count_csv(self, output_file="pair_count_matrix.csv"):
        students = sorted(self.pair_count.keys())
        
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the header row
            writer.writerow([""] + students)
            
            # Write each student's row
            for i, student in enumerate(students):
                row = [student]
                for j, other_student in enumerate(students):
                    if i > j:  # Only fill in the lower-left part
                        row.append(self.pair_count[student].get(other_student, 0))
                    else:  # Leave the top-right part empty
                        row.append("")
                writer.writerow(row)

    def save_groups_to_text(self, output_file="group_assignments.txt"):
        with open(output_file, "w") as file:
            for week_num, groups in enumerate(self.load_group_data(), start=1):
                if groups:  # Check that there is at least one group
                    group_size = len(groups[0])
                    file.write(f"Week {week_num} (Groups of {group_size})\n")
                else:
                    file.write(f"Week {week_num}\n")  # Handle case where there are no groups
                for group in groups:
                    file.write(", ".join(group) + "\n")
                file.write("\n")  # Add a blank line between weeks

    def load_group_data(self):
        # Helper function to load existing groups from JSON
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                data = json.load(file)
                return data["groups"]
        return []





def main():
    # Initialize the GroupAssigner with the specified files
    assigner = GroupAssigner(filename="group_data.json", students_file="students.txt")
    
    # Form groups of a specific size (e.g., 3 students per group)
    group_size = 4
    groups = assigner.form_groups(group_size=group_size)
    
    # Print the formed groups
    print("Groups:", groups)
    
    # Print how many times each student has worked with others
    assigner.print_pair_counts()

    # Generate the CSV output for pair counts
    assigner.generate_pair_count_csv()

    # Save the groups to a text file
    assigner.save_groups_to_text()


if __name__ == "__main__":
    main()
