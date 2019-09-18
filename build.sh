#! /usr/bin/env sh
# Create a symlink of bin/viper.py at /usr/local/bin/viper

# Get the absolute path of where script is running from
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

script_dir="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
script_path="$script_dir/run.sh"

# RETURN VARIABLE
ret=""

# ARGUMENTS
args="${@:2}" # All arguments except the first

# DESCRIPTION:
#	Where execution starts
#
main() {
    case $1 in
		setup )
			setup
		;;
		--help|help|-h )
			help
		;;
	esac

    exit 0
}

# Prints help message
help() {
	echo ""
	echo "============== VIPER BUILD UTILS ==================="
	echo ""
	echo " [USAGE] : sh build.sh [comand]"
	echo ""
	echo " [COMMAND] :"
	echo "    help  - print this help message"
	echo "    setup - make viper command available system-wide"
	echo ""
	echo "===================================================="
	echo ""
}

# Makes viper command available system-wide
setup() {
    local viper_sh_path="$script_dir/cli/viper.sh"
    local viper_py_path="$script_dir/cli/viper.py"

	display "Making viper.sh and viper.py executable"
	chmod 777 $viper_sh_path && chmod 777 $viper_py_path

	if [ "$?" -ne 0 ]; then
		exit 1
	fi

	displayln "Adding a link to viper.sh in /usr/local/bin"
	ln -s $viper_sh_path /usr/local/bin/viper

	if [ "$?" -ne 0 ]; then
		exit 2
	fi
}

# Prints message
display() {
	printf "::: $1 :::\n"
}

# Prints message with a newline
displayln() {
	printf "\n::: $1 :::\n"
}

main $*
