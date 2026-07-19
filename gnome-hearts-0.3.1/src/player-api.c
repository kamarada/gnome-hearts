/*
 *  Hearts - player-api.c
 *  Copyright 2006 Sander Marechal
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif
 
#include <Python.h>
#include "hearts.h"
#include "cfg.h"
#include "cards.h"
#include "ui.h"
#include "player-api.h"

/* Start python and load hearts.py */
void python_start(void)
{
	Py_Initialize();
	initplayer_api();
	PyObject *module = PyImport_AddModule("__main__");
	PyObject *dict = PyModule_GetDict(module);
	
	FILE* file = fopen(PYTHON_DIR"/gnome-hearts/hearts.py", "r");
	g_assert(file);
	PyRun_File(file, "hearts.py", Py_file_input, dict, dict);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	fclose(file);
}

/* Stop python */
void python_stop(void)
{
	Py_Finalize();
}

/* Python function that returns the value of the trick */
static PyObject* python_trick_get_score(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", trick_get_score(&game_trick));
}

/* Python function that returns if a card is valid or not */
static PyObject* python_is_valid(PyObject *self, PyObject *args)
{
	gint suit, rank, p;
	Card *card;
	
	/* Get the card and the player direction */
	if (!PyArg_ParseTuple(args, "(ii)i", &suit, &rank, &p))
		return NULL;

	/* find the card and return it's status */
	card = &g_array_index(game_deck, Card, CARD_ID(suit, rank));
	return Py_BuildValue("i", (int)game_is_valid_card(card, player[p]->hand, &game_trick));
}

/* register a class as an AI */
static PyObject *python_register_ai(PyObject *self, PyObject *args)
{
	gchar *name, *class;
	
	PyArg_ParseTuple(args, "ss", &name, &class);
	ui_add_ai_script(name, class);
			
	// Return None
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef player_api_methods[] = {
    {"trick_get_score", python_trick_get_score, METH_VARARGS, "Return the total vaule of the cards on the trick."},
    {"is_valid", python_is_valid, METH_VARARGS, "Check if a card is valid to play."},
    {"register_ai", python_register_ai, METH_VARARGS, "Register a player AI script in C."},
    {NULL, NULL, 0, NULL} /* sentinel */
};

/* Initialize the module */
PyMODINIT_FUNC initplayer_api(void)
{
	Py_InitModule("player_api", player_api_methods);
}
