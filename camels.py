from random import randint, shuffle


VERBOSE = False


class Game:
    def __init__(self, camels=None, init_state=None):
        _camels = self._infer_camels(camels, init_state)
        self.die = self._produce_camel_die(_camels)
        _state = self._infer_state(_camels, init_state)
        self.board = Board(_state)
        if VERBOSE:
            self.board.show()

    def one_round(self):
        for camel, steps in self.die():
            self.board.move_camel(camel, steps)

    def leaderboard(self):
        return self._leaderboard(self.board._pos_to_stack)

    @staticmethod
    def _leaderboard(pos_to_stack):
        positions = sorted(pos_to_stack)
        res = []
        for pos in positions:
            stack = pos_to_stack[pos]
            res.extend(list(stack.camels))
        return res

    def _infer_camels(self, camels, state):
        if state is not None:
            return self._extract_camels(state)
        return camels

    @staticmethod
    def _extract_camels(state):
        return [camel for stack in state.values()
                for camel in stack.camels]

    def _infer_state(self, camels, state):
        if state:
            return state
        return self._produce_init_state()

    def _produce_init_state(self):
        pos_to_stack = {}
        for camel, pos in self.die():
            pos_to_stack.setdefault(pos, CamelStack([])).attach(CamelStack([camel]))
        return pos_to_stack

    @staticmethod
    def _produce_camel_die(camels):
        game_camels = list(camels)

        def camel_die():
            shuffle(game_camels)
            steps = [randint(1, 3) for i in game_camels]
            return list(zip(game_camels, steps))

        return camel_die


class Board:
    def __init__(self, init_pos_to_stack):
        self.set_state(init_pos_to_stack)

    def set_state(self, camel_state):
        self._camel_to_pos = self._index_camel_stacks(camel_state)
        self._pos_to_stack = camel_state

    def show(self):
        sorted_pos = sorted(self._pos_to_stack)
        for pos in sorted_pos:
            stack = self._pos_to_stack[pos]
            print(pos, ":", stack.camels)
        print(self._camel_to_pos)

    def move_camel(self, camel, steps):
        if VERBOSE:
            print(camel, steps)
            self.show()
        curpos = self._camel_to_pos[camel]
        newpos = curpos + steps
        self._move_camel_from_to(camel, curpos, newpos)

    def _move_camel_from_to(self, camel, pos, newpos):
        oldstack_moved = self._detach_camelstack(pos, camel)
        self._attach_camelstack(oldstack_moved, newpos)
        self._update_index(oldstack_moved, newpos)

    def _detach_camelstack(self, pos, camel):
        oldstack = self._pos_to_stack[pos]
        oldstack_moved = oldstack.detach(camel)

        if oldstack.isempty():
            del self._pos_to_stack[pos]

        return oldstack_moved

    def _attach_camelstack(self, camelstack, newpos):
        target_stack = self._pos_to_stack.get(newpos)
        if not target_stack:
            self._pos_to_stack[newpos] = camelstack
        else:
            target_stack.attach(camelstack)

    def _update_index(self, moved_stack, newpos):
        for camel in moved_stack.camels:
            self._camel_to_pos[camel] = newpos

    @staticmethod
    def _index_camel_stacks(pos_to_stack):
        idx = {}
        for pos, stack in pos_to_stack.items():
            for camel in stack.camels:
                assert camel not in idx
                idx[camel] = pos
        return idx


class CamelStack:
    def __init__(self, camels):
        self.camels = camels

    def detach(self, camel):
        camel_idx = self.camels.index(camel)
        moved = self.camels[camel_idx:]
        self.camels = self.camels[:camel_idx]
        return CamelStack(moved)

    def attach(self, camelstack):
        self.camels.extend(camelstack.camels)

    def isempty(self):
        return not bool(self.camels)


def state_from_dict(pos_to_names):
    res = {}
    for pos, names in pos_to_names.items():
        res[pos] = CamelStack(names)
    return res


if __name__ == "__main__":
    VERBOSE = True
    init_pos = {1: ["red", "green", "yellow"],
                2: ["blue"],
                3: ["orange"]}
    init_state = state_from_dict(init_pos)
    game = Game(init_state=init_state)
    game.one_round()
