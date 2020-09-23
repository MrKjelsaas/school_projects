

class Course_grade:
    def set_assignment(self, assignment_number, grade):
        self.assignments[assignment_number-1] = grade

    def set_all_assignments(self, grade):
        for n in range(len(self.assignments)):
            self.assignments[n] = grade

    def set_exam_result(self, grade):
        self.final_exam = grade



class ACIT4420_2019(Course_grade):
    def __init__(self):
        # We treat false as the same as not delivered
        self.assignments = [False, False, False, False, False, False, False]
        self.final_exam = 0

    def get_grade(self):
        # If an assignment was not submitted then the final grade is F
        for n in range(len(self.assignments)):
            if self.assignments[n] == False:
                return "F"

        # If the final exam percentage is less than 40 percent then the final grade is F
        if self.final_exam < 40:
            return "F"

        # In all other cases the final exam and the graded assignments are added and the final grade is
        # evaulated using the normal scale
        if self.final_exam < 50:
            return "E"
        if self.final_exam < 60:
            return "D"
        if self.final_exam < 80:
            return "C"
        if self.final_exam < 90:
            return "B"
        return "A"

class ACIT4420_2020(Course_grade):
    def __init__(self):
        # We treat 0 as the same as not delivered
        self.assignments = [0, 0, 0, 0, 0, 0, 0]
        self.final_exam = 0
        self.assignment_weights = [0.05, 0.07, 0.1, 0.06, 0.07, 0.08, 0.07]
        self.final_exam_weight = 0.5

    def get_grade(self):
        # If an assignment was not submitted then the final grade is F
        for n in range(len(self.assignments)):
            if self.assignments[n] == 0:
                return "F"

        # If the sum percentage of the graded assignments is less than 40 percent then the final grade is F
        assignments_sum = 0
        for n in range(len(self.assignments)):
            assignments_sum += self.assignments[n] * self.assignment_weights[n]
        if 2*assignments_sum < 40:
            return "F"

        # If the final exam percentage is less than 40 percent then the final grade is F
        if self.final_exam < 40:
            return "F"

        # In all other cases the final exam and the graded assignments are added and the final grade is
        # evaulated using the normal scale
        if self.final_exam * self.final_exam_weight + assignments_sum < 50:
            return "E"
        if self.final_exam * self.final_exam_weight + assignments_sum < 60:
            return "D"
        if self.final_exam * self.final_exam_weight + assignments_sum < 80:
            return "C"
        if self.final_exam * self.final_exam_weight + assignments_sum < 90:
            return "B"
        return "A"



a = ACIT4420_2020()
a.set_all_assignments(70)
a.set_assignment(2, 100)
a.set_exam_result(76)
print(a.get_grade())

a2 = ACIT4420_2019()
a2.set_all_assignments(True)
a2.set_exam_result(76)
print(a2.get_grade())

b = ACIT4420_2020()
b.set_all_assignments(20)
b.set_assignment(2, 100)
b.set_exam_result(84)
print(b.get_grade())

b2 = ACIT4420_2019()
b2.set_all_assignments(True)
b2.set_exam_result(84)
print (b2.get_grade())
