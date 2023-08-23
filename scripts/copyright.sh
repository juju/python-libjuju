#!/bin/bash

supports_colors() {
	if [[ -z ${TERM} ]] || [[ ${TERM} == "" ]] || [[ ${TERM} == "dumb" ]]; then
		echo "NO"
		return
	fi
	if which tput >/dev/null 2>&1; then
		# shellcheck disable=SC2046
		if [[ $(tput colors) -gt 1 ]]; then
			echo "YES"
			return
		fi
	fi
	echo "NO"
}

red() {
	if [[ "$(supports_colors)" == "YES" ]]; then
		tput sgr0
		echo "$(tput setaf 1)${1}$(tput sgr0)"
		return
	fi
	echo "${1}"
}

run_copyright() {
	OUT=$(find . -name '*.py' | grep -v -E "./(docs|scripts|debian|juju-egg-info|.tox|.git|juju/client|tests/charm)|__init__" | sort | xargs grep -L -E '# (Copyright|Code generated)' || true)
	LINES=$(echo "${OUT}" | wc -w)
	if [ "$LINES" != 0 ]; then
		echo ""
		echo "$(red 'Found some issues:')"
		echo -e '\nThe following files are missing copyright headers'
		echo "${OUT}"
		exit 1
	fi
}

test_copyright() {
	echo "==> Copyright analysis"

	(
		# cd .. || exit

		# Check for copyright notices
		run_copyright
	)
}

test_copyright