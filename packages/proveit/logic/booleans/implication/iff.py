from proveit import Literal, Operation, USE_DEFAULTS
from proveit.logic.booleans.conjunction import compose
from .implies import Implies
from proveit import A, B, C
from proveit import TransitiveRelation

# if and only if: A => B and B => A


class Iff(TransitiveRelation):
    # The operator of the Iff operation
    _operator_ = Literal(
        string_format='<=>',
        latex_format=r'\Leftrightarrow',
        theory=__file__)

    # map left-hand-sides to Subset Judgments
    #   (populated in TransitivityRelation.derive_side_effects)
    known_left_sides = dict()
    # map right-hand-sides to Subset Judgments
    #   (populated in TransitivityRelation.derive_side_effects)
    known_right_sides = dict()

    def __init__(self, A, B):
        TransitiveRelation.__init__(self, Iff._operator_, A, B)
        self.A = A
        self.B = B

    def side_effects(self, judgment):
        '''
        Yield the TransitiveRelation side-effects (which also records known_left_sides
        and known_right_sides).  Also derive the left and right implications,
        derive the reversed version and attempt to derive equality.
        '''
        for side_effect in TransitiveRelation.side_effects(self, judgment):
            yield side_effect
        yield self.derive_left_implication  # B=>A given A<=>B
        yield self.derive_right_implication  # A=>B given A<=>B
        yield self.derive_reversed  # B<=>A given A<=>B
        # A=B given A<=>B (assuming A and B are in booleans)
        yield self.derive_equality

    def conclude(self, assumptions):
        '''
        Try to automatically conclude this bi-directional implication by
        reducing its operands to true/false.
        '''
        from . import iff_t_t, iff_t_f, iff_f_t, iff_f_f, true_iff_true, false_iff_false
        if self in {true_iff_true, false_iff_false}:
            # should be proven via one of the imported theorems as a simple
            # special case
            try:
                self.evaluation(assumptions)
            except BaseException:
                return self.prove()
        try:
            # try to prove the bi-directional implication via evaluation reduction.
            # if that is possible, it is a relatively straightforward thing to
            # do.
            return Operation.conclude(assumptions)
        except BaseException:
            pass
        try:
            # Use a breadth-first search approach to find the shortest
            # path to get from one end-point to the other.
            return TransitiveRelation.conclude(self, assumptions)
        except BaseException:
            pass

        # the last attempt is to introduce the Iff via implications each way, an
        # essentially direct consequence of the definition.
        return self.conclude_by_definition(assumptions)

    def conclude_negation(self, assumptions=USE_DEFAULTS):
        # implemented by Joaquin on 6/17/19
        from proveit.logic.booleans import FALSE, TRUE
        try:
            if self.A == TRUE and self.B == FALSE:
                from . import true_iff_false_negated, false_iff_true_negated
            elif self.B == TRUE and self.A == FALSE:
                from . import true_iff_false_negated, false_iff_true_negated
        except BaseException:
            pass

    def derive_left_implication(self, assumptions=USE_DEFAULTS):
        '''
        From (A<=>B) derive and return B=>A.
        '''
        from . import iff_implies_left
        return iff_implies_left.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def derive_left(self, assumptions=USE_DEFAULTS):
        '''
        From (A<=>B) derive and return A assuming B.
        '''
        from . import left_from_iff
        return left_from_iff.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def derive_right_implication(self, assumptions=USE_DEFAULTS):
        '''
        From (A<=>B) derive and return A=>B.
        '''
        from . import iff_implies_right
        return iff_implies_right.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def derive_right(self, assumptions=USE_DEFAULTS):
        '''
        From (A<=>B) derive and return B assuming A.
        '''
        from . import right_from_iff
        return right_from_iff.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def derive_reversed(self, assumptions=USE_DEFAULTS):
        '''
        From (A<=>B) derive and return (B<=>A).
        '''
        from . import iff_symmetry
        return iff_symmetry.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def apply_transitivity(self, other_iff, assumptions=USE_DEFAULTS):
        '''
        From A <=> B (self) and the given B <=> C (other_iff) derive and return
        (A <=> C) assuming self and other_iff.
        Also works more generally as long as there is a common side to the equations.
        '''
        from . import iff_transitivity
        assert isinstance(other_iff, Iff)
        if self.B == other_iff.A:
            # from A <=> B, B <=> C, derive A <=> C
            return iff_transitivity.instantiate(
                {A: self.A, B: self.B, C: other_iff.B}, assumptions=assumptions)
        elif self.A == other_iff.A:
            # from y = x and y = z, derive x = z
            return self.derive_reversed(
                assumptions).apply_transitivity(other_iff, assumptions)
        elif self.A == other_iff.B:
            # from y = x and z = y, derive x = z
            return self.derive_reversed(assumptions).apply_transitivity(
                other_iff.derive_reversed(assumptions))
        elif self.B == other_iff.B:
            # from x = y and z = y, derive x = z
            return self.apply_transitivity(
                other_iff.derive_reversed(assumptions))
        else:
            assert False, 'transitivity cannot be applied unless there is something in common in the equalities'

    def definition(self):
        '''
        Return (A <=> B) = [(A => B) and (B => A)] where self represents (A <=> B).
        '''
        from . import iff_def
        return iff_def.instantiate({A: self.A, B: self.B})

    def conclude_by_definition(self, assumptions=USE_DEFAULTS):
        '''
        Conclude (A <=> B) assuming both (A => B), (B => A).
        '''
        from . import iff_intro
        return iff_intro.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def evaluation(self, assumptions=USE_DEFAULTS, automation=True):
        '''
        Given operands that evaluate to TRUE or FALSE, derive and
        return the equality of this expression with TRUE or FALSE.
        '''
        from . import iff_t_t, iff_t_f, iff_f_t, iff_f_f  # IMPORTANT: load in truth-table evaluations
        return Operation.evaluation(self, assumptions, automation)

    def deduce_in_bool(self, assumptions=USE_DEFAULTS):
        '''
        Attempt to deduce, then return, that this 'iff' expression is in the set of BOOLEANS.
        '''
        from . import iff_closure
        return iff_closure.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)

    def derive_equality(self, assumptions=USE_DEFAULTS):
        '''
        From (A <=> B), derive (A = B) assuming A and B in BOOLEANS.
        '''
        from . import eq_from_iff, eq_from_mutual_impl
        # We must be able to prove this Iff to do this derivation --
        # then either eq_from_iff or eq_from_mutual_impl can be used.
        self.prove(assumptions=assumptions)
        # eq_from_mutual_impl may make for a shorter proof; do it both ways (if
        # both are usable)
        if not eq_from_iff.is_usable():
            return eq_from_mutual_impl.instantiate(
                {A: self.A, B: self.B}, assumptions=assumptions)
        eq_from_mutual_impl.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)
        return eq_from_iff.instantiate(
            {A: self.A, B: self.B}, assumptions=assumptions)
