
/*******************************************************************************
* INCLUDE FILES
*******************************************************************************/
/* This header file is included for the respective BSW module */
#raw
#include "Rte.h"
#include "Rte_Type.h"
#include "Rte_Main.h"
#include "Rte_SwcLaIntegrationFem.h"
#include "Rte_SwcLaMaster.h"
#end raw


/******************************************************************************
* Global Variables
******************************************************************************/
struct rteStubs_t rteStubs;


/*******************************************************************************
* RTE INIT FUNCTION DEFINITIONS
*******************************************************************************/


/*******************************************************************************
* FUNCTION DEFINITIONS
*******************************************************************************/
#for $func in $funcs_decl
 
$func["retval"] $func["name"]
$func["params"]["decl"]
{
	#for $val in $func["params"]["vals"]
	#if $val["is_pointer"]
	#if "Rte_Call_" in $func["name"]
	(void) RteMemCpy(${val["name"]}, &rteStubs.${func["name"]}_$val["name"], sizeof($val["type_basic"]))
	#else if "Rte_Read_" in $func["name"]
	(void) RteMemCpy(${val["name"]}, &rteStubs.${func["name"]}_$val["name"], sizeof($val["type_basic"]))
	#else if "Rte_Write_" in $func["name"]
	(void) RteMemCpy(&rteStubs.${func["name"]}_$val["name"], ${val["name"]}, sizeof($val["type_basic"]))
	#end if
	#else
	rteStubs.${func["name"]}_$val["name"] = $val["name"];
	#end if
	#end for

	return RTE_E_OK;
}
#end for