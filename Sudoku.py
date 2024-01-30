import random


class Sudoku:
    def __init__(self, a):
        self.a = a
        self.process = False

    def line(self, k):
        return set(self.a[k]) - {0}

    def column(self, k):
        return set([s[k] for s in self.a]) - {0}

    def cube(self, sel):
        sel = (sel[0] // 3 * 3, sel[1] // 3 * 3)
        return set.union(*[set(s[sel[1]: sel[1] + 3]) for s in self.a[sel[0]: sel[0] + 3]]) - {0}

    def applicants(self, sel):
        i, j = sel
        if self.a[i][j] == 0:
            return {i for i in range(1, 10)} - self.cube(sel) - self.line(i) - self.column(j)
        return {}

    def predict(self, sel, autofill=False):
        i, j = sel
        app = self.applicants((i, j))
        if len(app) > 1:
            for k in app:
                if len(self.ex_line(k, i)) == 1 or len(self.ex_column(k, j)) == 1 or len(self.ex_cube(k, (i, j))) == 1:
                    if autofill:
                        self.a[i][j] = k
                    return k
        elif len(app) == 1:
            k = app.pop()
            if autofill:
                self.a[i][j] = k
            return k
        return False

    def check_map(self):
        for i in range(9):
            for j in range(9):
                if self.a[i][j] != 0:
                    k = self.a[i][j]
                    self.a[i][j] = 0
                    if k in self.applicants((i, j)):
                        self.a[i][j] = k
                    else:
                        return False
        return True

    def full_predict(self, autofill=False):
        for i in range(9):
            for j in range(9):
                self.predict((i, j), autofill=autofill)
        return False

    def ex_line(self, k, i):
        return {j for j in range(9) if k in self.applicants((i, j))}

    def ex_column(self, k, j):
        return {i for i in range(9) if k in self.applicants((i, j))}

    def ex_cube(self, k, sel):
        sel = (sel[0] // 3 * 3, sel[1] // 3 * 3)
        return set.union(*[{(i, j) for j in range(3) if k in self.applicants((sel[0] + i, sel[1] + j))} for i in range(3)])

    def deep_full_predict(self):
        min_app, min_sel = {i for i in range(10)}, ()
        for i in range(9):
            for j in range(9):
                app = self.applicants((i, j))
                if self.a[i][j] == 0 and len(app) < len(min_app):
                    min_sel, min_app = (i, j), app

        if not min_sel:
            return False

        vs = []
        for v in min_app:
            s = Sudoku([e.copy() for e in self.a])
            s.a[min_sel[0]][min_sel[1]] = v

            while s.full_predict(autofill=True):
                pass

            err, full = False, True
            for i in range(9):
                for j in range(9):
                    if s.a[i][j] == 0:
                        full = False
                        if not s.applicants((i, j)):
                            err = True

            if full:
                return s.a
            elif not err:
                vs.append(s)

        random.shuffle(vs)
        for s in vs:
            res = s.deep_full_predict()
            if res:
                return res
        return False

    def generate_map(self):
        self.process = True
        a = list(set.union(*[set((i, j) for j in range(9)) for i in range(9)]))
        n = [i for i in range(9)]
        self.a = [[0] * 9 for _ in range(9)]

        random.shuffle(a)
        for i, j in a[:15]:
            k = random.choice(n)
            while k not in self.applicants((i, j)):
                k = random.choice(n)
            self.a[i][j] = k

        self.a = self.deep_full_predict()
        random.shuffle(a)
        for i, j in a:
            k = self.a[i][j]
            self.a[i][j] = 0
            if self.predict((i, j)):
                continue
            else:
                self.a[i][j] = k
        self.process = False

    def fill_map(self):
        self.process = True
        if not self.check_map():
            self.process = False
            return False

        full = self.deep_full_predict()
        if full:
            self.a = full
        self.process = False
        return bool(full)
