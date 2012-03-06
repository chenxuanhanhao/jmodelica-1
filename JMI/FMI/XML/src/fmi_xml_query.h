/*
    Copyright (C) 2012 Modelon AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef FMI_XML_QUERY_H
#define FMI_XML_QUERY_H

#include <jm_vector.h>
#include <jm_stack.h>
#include <fmi_xml_variable.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Query below has the following syntax:
  query =   elementary_query
                  | '(' query ')'
                  | query 'or' query
                  | query 'and' query
                  | 'not' query
  elementary_query =  "name" '=' <string>
                    | "quantity" '=' <string>
                    | "basetype" '=' (real| integer | enumeration |boolean |string)
                    | "type" '=' <string>
                    | "unit" '=' <string>
                    | "displayUnit" '=' <string>
                    | "fixed" '=' ("true"|"false")
                    | "hasStart" '='  ("true"|"false")
                    | "isAlias"
                    | "alias" '=' ['-']<variable name> (negative value for negated-aliases)

Example: "name='a.*' & fixed=false"
*/

#define FMI_XML_Q_ELEMENTARY(HANDLE) \
    HANDLE(name) \
    HANDLE(unit) \

/*
    HANDLE(type) \
    HANDLE(fixed) \
    HANDLE(hasstart) \
    HANDLE(isalias) 
    HANDLE(alias)
    HANDLE(basetype) \
    HANDLE(displayunit) \
*/

typedef enum fmi_xml_elementary_enu_t {
#define FMI_XML_Q_ELEMENTARY_PREFIX(elem) fmi_xml_q_elmentary_enu_##elem,
    FMI_XML_Q_ELEMENTARY(FMI_XML_Q_ELEMENTARY_PREFIX)
    fmi_xml_elementary_enu_num
} fmi_xml_elementary_enu_t;

typedef struct fmi_xml_q_context_t fmi_xml_q_context_t;
typedef struct fmi_xml_q_terminal_t fmi_xml_q_terminal_t;

typedef int (*fmi_xml_q_scan_elementary_ft)(fmi_xml_q_context_t*, fmi_xml_q_terminal_t* term);

#define FMI_XML_Q_ELEMENTARY_DECLARE_SCAN(name) int fmi_xml_q_scan_elementary_##name(fmi_xml_q_context_t*, fmi_xml_q_terminal_t* term);
FMI_XML_Q_ELEMENTARY(FMI_XML_Q_ELEMENTARY_DECLARE_SCAN)


typedef int (*fmi_xml_q_eval_elementary_ft)(fmi_xml_variable_t* var, fmi_xml_q_terminal_t* term);

#define FMI_XML_Q_ELEMENTARY_DECLARE_EVAL(name) int fmi_xml_q_eval_elementary_##name(fmi_xml_variable_t* var, fmi_xml_q_terminal_t* term);
FMI_XML_Q_ELEMENTARY(FMI_XML_Q_ELEMENTARY_DECLARE_EVAL)

typedef enum fmi_xml_q_term_enu_t {
	fmi_xml_q_term_enu_elementary,
	fmi_xml_q_term_enu_LP,
	fmi_xml_q_term_enu_RP,
	fmi_xml_q_term_enu_OR,
	fmi_xml_q_term_enu_AND,
	fmi_xml_q_term_enu_NOT,
	fmi_xml_q_term_enu_END,
	fmi_xml_q_term_enu_TRUE,
	fmi_xml_q_term_enu_FALSE
} fmi_xml_q_terminal_enu_t;


struct fmi_xml_q_terminal_t {
	fmi_xml_q_terminal_enu_t kind;

	fmi_xml_elementary_enu_t specific;

	int param_i;
	double param_d;
	void* param_p;
	char* param_str;

};

jm_vector_declare_template(fmi_xml_q_terminal_t)

typedef jm_vector(fmi_xml_q_terminal_t) fmi_xml_q_term_vt;

typedef struct fmi_xml_q_expression_t fmi_xml_q_expression_t;

struct fmi_xml_q_expression_t {
    jm_vector(jm_voidp) expression;

    jm_vector(jm_voidp) stack;

    fmi_xml_q_terminal_t termFalse, termTrue;
    fmi_xml_q_term_vt terms;
	jm_vector(char) strbuf;
};

struct fmi_xml_q_context_t {
    jm_vector(jm_name_ID_map_t) elementary_map;

	jm_string query;

	size_t qlen;
	int curCh;

	jm_vector(char) buf;

	fmi_xml_q_expression_t expr;
};

void fmi_xml_q_init_context(fmi_xml_q_context_t*, jm_callbacks* cb);
void fmi_xml_q_free_context_data(fmi_xml_q_context_t*);
int fmi_xml_q_filter_variable(fmi_xml_variable_t* var, fmi_xml_q_expression_t* );
int fmi_xml_q_parse_query(fmi_xml_q_context_t* context, jm_string query);

#ifdef __cplusplus
}
#endif
#endif /* FMI_XML_QUERY_H */
