if [[ ! `echo $0 | grep oh-my-zsh` ]]; then
  RESOURCES_DIR=$1
  LIB_DIR=$RESOURCES_DIR/plugin_managers/lib

  source $LIB_DIR/async_prompt.zsh
  source $LIB_DIR/git.zsh
  source $LIB_DIR/prompt_info_functions.zsh
  source $LIB_DIR/theme-and-appearance.zsh
  source $LIB_DIR/directories.zsh
fi

