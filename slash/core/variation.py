from numbers import Number
import string
from .._compat import string_types

_PRINTABLE_TYPES = (Number,) + string_types
_PRINTABLE_CHARS = set(string.ascii_letters) | set(string.digits) | set("-_")

class Variations(object):
    def __init__(self):
        self._current_variation = None
        self._prev_variation = None

    def get_current_variation(self):
        return self._current_variation

    def set_current_variation(self, new_variation):
        if new_variation is None:
            self._prev_variation = self._current_variation
        self._current_variation = new_variation

    def is_param_variation_changed(self, param_id):
        if self._current_variation == self._prev_variation:
            return False
        if self._current_variation is None or self._prev_variation is None:
            return True
        [current_value, prev_value] = [x.param_value_indices.get(param_id, None) for x in [self._current_variation, self._prev_variation]]
        return current_value != prev_value

    def get_variation_from_param_id(self, param_id):
        return self._current_variation.param_value_indices[param_id]

class Variation(object):

    """Represents a single variation of parameter points. A variation is merely a mapping of fixture ids to their values.
    This mostly applies for parametrization fixtures. The other fixtures follow since they are either constant
    or indirectly depend on parametrization"""

    def __init__(self, store, param_value_indices, param_name_bindings):
        """
        :param name_bindings: dictionary mapping parameter name to its id
        """
        super(Variation, self).__init__()
        self._store = store
        self.param_value_indices = param_value_indices
        self.id = {}
        self.values = {}
        self.labels = {}
        for param_name, param in param_name_bindings.items():
            value_index = self.id[param_name] = param_value_indices[param.info.id]
            self.values[param_name] = param.get_value_by_index(value_index)
            self.labels[param_name] = param.values[value_index].label
        self.safe_repr = self._get_safe_repr()

    def _get_safe_repr(self):
        returned = {}
        for name, value in self.values.items():
            returned[name] = self._format_parameter_value_safe(name, value)
        return ','.join('{}={}'.format(key, returned[key]) for key in sorted(returned))

    def _format_parameter_value_safe(self, name, value):
        label = self.labels[name]

        if isinstance(label, str):
            return label
        value = str(value)
        if self._is_printable(value):
            return str(value)
        return '{}{}'.format(name, label)

    def _is_printable(self, value):
        if not isinstance(value, _PRINTABLE_TYPES):
            return False
        return _PRINTABLE_CHARS.issuperset(value)

    def has_value_for_parameter(self, param_id):
        return param_id in self.param_value_indices

    def get_param_value(self, param):
        return self._store.get_value(self, param)

    def __eq__(self, other):
        if isinstance(other, Variation):
            other = other.param_value_indices
        if not isinstance(other, dict):
            return NotImplemented
        return self.param_value_indices == other

    def __ne__(self, other):
        return not (self == other)  # pylint: disable=superfluous-parens,unneeded-not

    def __repr__(self):
        return 'Variation({})'.format(', '.join('{}={}'.format(key, value) for key, value in self.param_value_indices.items()))

    def __nonzero__(self):
        return bool(self.param_value_indices)

    __bool__ = __nonzero__
