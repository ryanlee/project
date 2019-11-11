RECIPE SYNTAX

steps : [
	step,
	step,
	[step, step, step],
] 
# use array to support order and parallel, only downside is parallel steps don't have a global name, but could be workaround using level1.level2 syntax on name?
# OR, sharing same prefix. means parallel?

types: {
	regression: {
	regexp:
	script:
	}
}

step = { # could be single table (add ID?)
	name:<build> (level1.level2.level3) so tests expanded could be grouped
	type: regression (could expand)
	
	# python keywords :
	try: <script>
	except: <script> or {
		result1: <script>
		result2: <script>
	}
	else: <script>
	finally: <script>
	
	log_path: "save this so external extension could analyze it"
	
	options/params: "whatever…"
	
	env:
	tools: ?
	
	timeout: 1m
	retry:0 
	}
	
<script> add a pre-command?
bash 'cmd'
bsub -q batch 'cmd'
input 'cmd'

steps:[
{name:build, try:"compile" },
{name:test.sanity, try:"sanity test" },
{name:compile_groups, try:"${group} compile", expand="group" } #	need to unique groups before expanding
[
	{name:test.group1, try:"group1 test" },
	{name:test.group2, try:"group2 test ${test}",type=regression, expand='name' } #	expand to multiple jobs
	[ 
	  {name:test.group3.compile, try:"group3 compile" },
	  {name:test.group3.test, try:"group1 test", type=regression , expand='name'} #	expand to multiple jobs
	]
]
]

*generic expand*
# this could make regression type jobs really generic, with nothing related to regression at all.
	1. all testplan feed into args, and only expand!="" care about it?
	2. add all optional columns as single field into the job, the web could expose them into separate fields.

these could be covered in generic expand
read in all testplan and merge them.
count how many step.expand, loop through and make step->job expansion.

*result analysis*
extension/ or simply regexp pairs?

analyze logfile : 
	log_path	result, result_details	may be just a list of regexp instead of script?

