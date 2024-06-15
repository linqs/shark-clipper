'use strict;'

function randomHex(bits = 64) {
    let intCount = Math.ceil(bits / 32);
    let ints = new Uint32Array(intCount);

    self.crypto.getRandomValues(ints);

    let result = '';
    ints.forEach(function(value) {
        result += value.toString(16);
    });

    return result;
}
