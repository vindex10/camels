from random import randint, shuffle


VERBOSE = False


class Game:
    def __init__(self, camels=None, init_state=None):
        _camels = self._infer_camels(camels, init_state)
        self.die = CamelDie(_camels)
        _state = self._infer_state(self.die, init_state)
        self.board = Board(_state)
        if VERBOSE:
            self.board.show()

    def one_step(self):
        camel, steps = self.die.roll_once()
        self.board.move_camel(camel, steps)

    def finish_round(self):
        for camel, steps in self.die.roll_finish_round():
            self.board.move_camel(camel, steps)

    def leaderboard(self):
        return flatten_state(self.board.state.state)

    def _infer_camels(self, camels, state):
        if state is not None:
            return self._extract_camels(state)
        return list(camels)

    @staticmethod
    def _extract_camels(state):
        return [camel for stack in state.pos_to_stack.values()
                for camel in stack.camels]

    @classmethod
    def _infer_state(cls, die, state):
        if state:
            return state.copy()
        return cls._produce_init_state(die)

    @staticmethod
    def _produce_init_state(die):
        pos_to_stack = {}
        for camel, pos in die.roll_finish_round():
            pos_to_stack.setdefault(pos, CamelStack([])).attach(CamelStack([camel]))
        return State(pos_to_stack)


class CamelDie:
    MIN_STEPS = 1
    MAX_STEPS = 3

    def __init__(self, camels, die_state=None):
        self._camels = list(camels)
        self.state = list(die_state) if die_state is not None else None
        if die_state is None:
            self._reset_state()

    def roll_once(self):
        try:
            camel = self.state.pop()
        except IndexError:
            self._reset_state()
            camel = self.state.pop()

        steps = randint(self.MIN_STEPS, self.MAX_STEPS)
        return camel, steps

    def roll_finish_round(self):
        res = []
        while self.state:
            camel = self.state.pop()
            steps = randint(self.MIN_STEPS, self.MAX_STEPS)
            res.append((camel, steps))
        self._reset_state()
        return res

    def _reset_state(self):
        self.state = list(self._camels)
        shuffle(self.state)


class Board:
    def __init__(self, init_state):
        self.state = MoveableState().consume(init_state.copy())

    def show(self):
        sorted_pos = sorted(self.state.state.pos_to_stack)
        for pos in sorted_pos:
            stack = self.state.state.pos_to_stack[pos]
            print(pos, ":", stack.camels)
        print(self.state._camel_to_pos)

    def move_camel(self, camel, steps):
        if VERBOSE:
            print(camel, steps)
            self.show()
        curpos = self.state.get_camel_pos(camel)
        newpos = curpos + steps
        self.state.move_camel_from_to(camel, curpos, newpos)


class State:
    def __init__(self, pos_to_stack):
        self.pos_to_stack = self._copy(pos_to_stack)

    def get(self):
        return self.pos_to_stack

    def copy(self):
        return State(self._copy(self.pos_to_stack))

    @staticmethod
    def _copy(pos_to_stack):
        res = {}
        for pos, stack in pos_to_stack.items():
            res[pos] = stack.copy()
        return res

    @classmethod
    def from_dict(cls, camel_dict):
        res = {}
        for pos, camels in camel_dict.items():
            res[pos] = CamelStack(list(camels))
        return State(res)


class MoveableState:
    def __init__(self):
        # use consume() to init state. improves readability
        self._camel_to_pos = None
        self.state = None

    def consume(self, ref_state):
        self._camel_to_pos = self._index_camel_stacks(ref_state)
        self.state = ref_state
        return self

    def get(self):
        return self.state()

    def get_camel_pos(self, camel):
        return self._camel_to_pos[camel]

    def move_camel_from_to(self, camel, pos, newpos):
        oldstack_moved = self._detach_camelstack(pos, camel)
        self._attach_camelstack(oldstack_moved, newpos)
        self._update_index(oldstack_moved, newpos)

    def _detach_camelstack(self, pos, camel):
        oldstack = self.state.pos_to_stack[pos]
        oldstack_moved = oldstack.detach(camel)

        if oldstack.isempty():
            del self.state.pos_to_stack[pos]

        return oldstack_moved

    def _attach_camelstack(self, camelstack, newpos):
        target_stack = self.state.pos_to_stack.get(newpos)
        if not target_stack:
            self.state.pos_to_stack[newpos] = camelstack
        else:
            target_stack.attach(camelstack)

    def _update_index(self, moved_stack, newpos):
        for camel in moved_stack.camels:
            self._camel_to_pos[camel] = newpos

    @staticmethod
    def _index_camel_stacks(state):
        idx = {}
        for pos, stack in state.pos_to_stack.items():
            for camel in stack.camels:
                assert camel not in idx
                idx[camel] = pos
        return idx


class CamelStack:
    def __init__(self, camels):
        self.camels = camels

    def copy(self):
        return CamelStack(list(self.camels))

    def detach(self, camel):
        camel_idx = self.camels.index(camel)
        moved = self.camels[camel_idx:]
        self.camels = self.camels[:camel_idx]
        return CamelStack(moved)

    def attach(self, camelstack):
        self.camels.extend(camelstack.camels)

    def isempty(self):
        return not bool(self.camels)


def flatten_state(state):
    pos_to_stack = state.pos_to_stack
    positions = sorted(pos_to_stack)
    res = []
    for pos in positions:
        stack = pos_to_stack[pos]
        res.extend(list(stack.camels))
    return res


if __name__ == "__main__":
    VERBOSE = True
    # init_pos = {1: ["red", "green", "yellow"],
                # 2: ["blue"],
                # 3: ["orange"]}
    # init_state = state_from_dict(init_pos)
    # game = Game(init_state=init_state)
    game = Game(['a', 'b', 'c'])
    game.finish_round()
