#!/bin/bash

# detect env
if [ "${USER}" == "ec2-user" ]; then
	export ENV="AWS"
elif [[ ${HOSTNAME} == *.compute.internal ]]; then
	export ENV="AWS"

elif [ "${USER}" == "mtk21506" ]; then
	export ENV="mtk"

elif [ "${USER}" == "b06542" ]; then
	export ENV="FSL"

elif [ "${HOSTNAME}" == "NUC" ]; then
	export ENV="NUC"
elif [ "${HOSTNAME}" == "NAS" ]; then
	export ENV="NAS"

else # if ${USER} == "ryan" then
	echo "unknown ENV for '${USER}' @ '${HOSTNAME}'"
	export ENV=''
	# endif
fi

REPO=https://ryan-li@bitbucket.org/ryan-li/home.git

if test $# -ge 1; then
	T=$(realpath $1)
else
	T=~
fi

if [ ! -d ${T} ]; then
	mkdir -p ${T}
fi
cd ${T}
echo "=========================="
echo "Nesting under ${T} ..."
echo "=========================="

function input(){
	read -p "$1 ? " -n 1 -r
	if ! [[ $REPLY =~ ^[Yy]$ || $REPLY == '' ]]; then
		return 0
	else
		return 1
	fi
}

#####################################################################################	
##  METHOD 1
#####################################################################################	
function nest_git(){
	if test $# -ge 1; then
		t="$1"
	else
		t=~
	fi
	cd ${t}

	echo "=> DOWNLOAD $REPO"
	rm -rf .git/

	echo "-> add repo"
	git init
	git remote add origin $REPO
	git config remote.origin.push HEAD # NOTOWKR when git push: fatal: The current branch master has multiple upstream branches, refusing to push.
	echo "-> fetch repo"
	git fetch;

	echo "-> checkout repo"
	git checkout -f master
}

#####################################################################################	
##  # METHOD 2
#####################################################################################	
##  NEST=${T}/.nest
##  
##  echo "=> clone git into ${NEST}"
##  rm -rf ${NEST}
##  git clone ${REPO} ${NEST} --no-checkout 
##  
##  echo "=> move git into ${T}"
##  rm -rf ${T}/.git; mv ${NEST}/.git ${T}; rm -rf ${NEST}
##  # mv -fv ${NEST}/* ${NEST}/.* ${T}/
##  
##  exit
##  echo "=> checkout"
##  cd ${T}
##  # git reset HEAD
##  # git reset --hard HEAD 
##  git checkout master -f
##  exit
##  git config remote.origin.push HEAD


#####################################################################################	
# METHOD 3
#####################################################################################	
##  git clone --bare $REPO .git
##  git config core.bare false
##  git reset

function nest_ssh() {
	if test $# -ge 1; then
		t="$1"
	else
		t=~
	fi
	echo "=> FIX .SSH PERMISSION"
	chmod go-rwx -R ${t}/.ssh/
}

function nest_shrc() {
	if test $# -ge 1; then
		t="$1"
	else
		t=~
	fi
	for sh in bash csh; do
		shrc=.${sh}rc
		ushrc=.${sh}rc.user
		echo "=> setup $shrc"
		if [ -f ${t}/$shrc ]; then
			grep $ushrc ${t}/$shrc > /dev/null
			if test $? -ne 0 ; then
				echo "\t-> add $ushrc"
				if [ "$sh" == "bash" ]; then
					echo "[ -f ${t}/$ushrc ] && source ${t}/$ushrc" >> ${t}/$shrc
				elif [ "$sh" == "csh" ]; then
					echo "if (-e ${t}/$ushrc) source ${t}/$ushrc" >> ${t}/$shrc
				fi
			fi
		fi
	done                  
}

function nest_vim() {
echo "-> install all vim plugs"
vim +PlugInstall +qall
# cp -f $T/_vim/plugged/fzf/bin/* $T/bin/ 
}


function nest_submodule () {
	echo "-> pull submodules ... (not including src/private)"
	git submodule init    ~/pkg/* ~/src/public; 
	git submodule update  ; 
	git submodule status  ; 
	git submodule foreach git checkout master 
	git submodule foreach git pull origin master
}

function nest_compile () {
	echo "-> compiling vim"
	sudo apt install libncurses-dev 
	~/.vim/tools/compile.sh
}

nest_git $T
nest_ssh $T
nest_shrc $T
nest_vim $T
