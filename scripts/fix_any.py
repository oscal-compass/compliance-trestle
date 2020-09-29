"""Simple script to fix Any's in bad files created by datamodel-code-generator."""

# This relies on datamodel-codegen 0.5.28 to create classes that work,
#   but don't do much checking.
# This is because the generated classes rely on Any - which does no checking.
# This script changes the Any's appropriately from the plural form of the needed
#   class to the singular form.
# It then reorders the classes so there are no forwards required.
# This reordering is optimistic and assumes there is nothing circular involved -
#   and that there are no side effect classes that become forwarded.
# This script is called by gen_oscal.py when models are generated

pattern1 = 'ies: Optional[Dict[str, Any]]'
pattern2 = 's: Optional[Dict[str, Any]]'
class_header = 'class '


class ClassText():
    """Hold class text as named blocks with references to the added classes."""

    def __init__(self, first_line):
        self.lines = [first_line.rstrip()]
        n = first_line.find('(')
        self.name = first_line[len(class_header):n]
        self.refs = set()

    def add_line(self, line):
        self.lines.append(line)

    def add_ref(self, ref_name):
        self.refs.add(ref_name)

    @staticmethod
    def find_index(class_text_list, name):
        nclasses = len(class_text_list)
        for i in range(nclasses):
            if class_text_list[i].name == name:
                return i
        return -1


def swap_ref(class_list, ref):
    """Swap a reference class definition so it is before first reference."""
    ref_index = ClassText.find_index(class_list, ref)  # get index of class definition
    nclasses = len(class_list)
    did_swap = False
    for i in range(nclasses):                          # get index of first ref
        if ref in class_list[i].refs:
            if i < ref_index:                          # need to swap
                cdef = class_list.pop(ref_index)
                class_list.insert(i, cdef)
                did_swap = True
                break
    return class_list, did_swap


def get_cap_stem(s, clip):
    """Extract stem part of plural form from first word on line."""
    n = 0
    while s[n] == ' ':
        n += 1
    cap = s[n].upper()
    n += 1
    while s[n + clip] != ':':
        if s[n] == '_':
            cap += s[n + 1].upper()
            n += 2
            continue
        cap += s[n]
        n += 1
    return cap


def fix_file(fname):
    """Fix the Anys in this file."""
    ref_class_names = set()
    all_classes = []
    header = []

    class_text = None
    done_header = False

    with open(fname, 'r') as infile:
        for r in infile.readlines():
            if r.find(class_header) == 0:             # start of new class
                done_header = True
                if class_text is not None:            # we are done with current class so add it
                    all_classes.append(class_text)
                class_text = ClassText(r)
            else:
                if not done_header:                   # still in header
                    header.append(r.rstrip())
                else:                                 # in body of class looking for Any's
                    n1 = r.find(pattern1)
                    n2 = r.find(pattern2)
                    if n1 != -1:                      # ies plural
                        tail = r[(n1 + len(pattern1)):]
                        cap_singular = get_cap_stem(r, 3) + 'y'
                        ref_class_names.add(cap_singular)
                        class_text.add_ref(cap_singular)
                        r = r[:(n1 + len(pattern1) - 5)] + cap_singular + ']]' + tail
                    elif n2 != -1:                    # s plural
                        tail = r[(n2 + len(pattern2)):]
                        cap_singular = get_cap_stem(r, 1)
                        ref_class_names.add(cap_singular)
                        class_text.add_ref(cap_singular)
                        r = r[:(n2 + len(pattern2) - 5)] + cap_singular + ']]' + tail
                    class_text.add_line(r.rstrip())

    all_classes.append(class_text)                    # don't forget final class
    ref_class_names = sorted(ref_class_names)

    no_swaps = False

    while not no_swaps:
        no_swaps = True
        for ref in ref_class_names:
            all_classes, did_swap = swap_ref(all_classes, ref)
            if did_swap:
                no_swap = False

    with open(fname, 'w') as out_file:
        out_file.write('# modified by fix_any.py\n')
        out_file.writelines('\n'.join(header) + '\n')
        for c in all_classes:
            out_file.writelines('\n'.join(c.lines) + '\n')
