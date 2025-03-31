Use of ``install`` now preserves previously registered module configurations on
new icecream truck being installed into the Python builtins. This allows
libraries to register module configurations before applications install an
icecream truck, thus providing greater flexibility around initialization-time
and runtime sequencing of operations.

Note that this is a mildly breaking change in the sense that installation would
refuse to proceed if a matching name already existed in the ``builtins``
module.
