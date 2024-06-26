#!/bin/bash

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"

function main() {
    set -e
    trap exit SIGINT

    cd "${THIS_DIR}"

    python -m sharkclipper.cli.server $@
    return $?
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
