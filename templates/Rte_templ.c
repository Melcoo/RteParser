
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
	rteStubs.${func["name"]}_$val["name"] = $val["name"];
	#end for

	return RTE_E_OK;
}
#end for