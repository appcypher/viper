#! /usr/bin/env sh

# Get the absolute path of where script is running from
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

script_dir="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
script_path="$script_dir/run.sh"

# Get viper cli script path
viper_py_path="$script_dir/viper.py"

# Get current working directory
cur_dir=`pwd`

# Cd into project directory
cd "$script_dir/.."

# Run viper and pass its arguments to it
pipenv run -- $viper_py_path $*

# Cd back to original directory
cd $cur_dir
