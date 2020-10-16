
/*******************************************************************************
* INCLUDE FILES
*******************************************************************************/
/* This header file is included for the respective BSW module */
#raw
#include "Rte.h"
#include "Rte_SwcLaIntegrationFem.h"
#undef RTE_APPLICATION_HEADER_FILE
#include "Rte_SwcLaMaster.h"
#end raw


/*******************************************************************************
** Rte #DEFINES USED FOR INITIALISATION OF GLOBAL VARIABLES                   **
*******************************************************************************/

#raw
#define RTE_E_OK  0
#end raw


/******************************************************************************
* Global Variables
******************************************************************************/
rteStubs_t rteStubs;


/******************************************************************************
* Local Variables
******************************************************************************/
#set $types = []
#for $func in $funcs_decl
#for $val in $func["params"]["vals"]
#if func["common_name"] == ''
<%type = func["name"] + '_' + val["name"]%>#slurp
#else
<%type = func["common_name"] + '_' + val["name"]%>#slurp
#end if
#if $type not in $types
<%psize = '[' + str(len(func["defval"])) + ']'%>#slurp
#if len($func["defval"]) > 1
#set $defval = ''
<%for dv in func["defval"]: defval = defval + dv + ', '%>#slurp
<%defval = defval[:-2]%>#slurp
$val["type_basic"] ${type}_Default$psize = {$defval};
#end if
$types.append($type)#slurp
#end if
#end for
#end for


/*******************************************************************************
* RTE INIT FUNCTION DEFINITIONS
*******************************************************************************/

#raw
void RteMemCpy(const void* dest, const void* src, uint32 size)
{
	uint32 i=0;
	for (i=0; i < size; i++)
	{
		((uint8*)dest)[i] = ((uint8*)src)[i];
	}
}
#end raw

void Rte_InitStubs(void)
{
	#set $types = []
	#for $func in $funcs_decl
	#if "Rte_Call_" in $func["name"]
	#for $val in $func["params"]["vals"]
#if func["common_name"] == ''
<%type = func["name"] + '_' + val["name"]%>#slurp
#else
<%type = func["common_name"] + '_' + val["name"]%>#slurp
#end if
	#if $type not in $types
	#if len($func["defval"]) < 2
	rteStubs.$type = $func["defval"][0];
	#else
<%size = len(func["defval"])%>#slurp
	(void) RteMemCpy(&rteStubs.${type}[0], &rteStubs.${type}_Default[0], $size); 
	#end if
$types.append($type)#slurp
	#end if
	#end for
	#end if
	#end for
}

/*******************************************************************************
* FUNCTION DEFINITIONS
*******************************************************************************/
#for $func in $funcs_decl
 
$func["retval"] $func["name"]
$func["params"]["decl"]
{
	#for $val in $func["params"]["vals"]
	#if func["common_name"] == ''
<%fname = func["name"]%>#slurp
	#else
<%fname = func["common_name"]%>#slurp	
	#end if
	#if $val["is_pointer"]
<%size = len(func["defval"])%>#slurp
	#if "Rte_Call_" in $func["name"]
	#if $size<2
	(void) RteMemCpy(${val["name"]}, &rteStubs.${fname}_$val["name"], sizeof($val["type_basic"]));
	#else
	(void) RteMemCpy(${val["name"]}, &rteStubs.${fname}_${val["name"]}[0], sizeof(rteStubs.${fname}_$val["name"])/sizeof($val["type_basic"]));
	#end if
	#else if "Rte_Read_" in $func["name"]
	#if $size<2
	(void) RteMemCpy(${val["name"]}, &rteStubs.${fname}_$val["name"], sizeof($val["type_basic"]));
	#else
	(void) RteMemCpy(${val["name"]}, &rteStubs.${fname}_${val["name"]}[0], sizeof(rteStubs.${fname}_$val["name"])/sizeof($val["type_basic"]));
	#end if
	#else if "Rte_Write_" in $func["name"]
	#if $size<2
	(void) RteMemCpy(&rteStubs.${fname}_$val["name"], ${val["name"]}, sizeof($val["type_basic"]));
	#else
	(void) RteMemCpy(&rteStubs.${fname}_${val["name"]}[0], ${val["name"]}, sizeof(rteStubs.${fname}_$val["name"])/sizeof($val["type_basic"]));
	#end if
	#end if
	#else
	rteStubs.${fname}_$val["name"] = $val["name"];
	#end if
	#end for

	return RTE_E_OK;
}
#end for

