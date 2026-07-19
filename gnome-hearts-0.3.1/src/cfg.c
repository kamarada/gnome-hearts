/*
 *  Hearts - cfg.c
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

/* Must be inlcuded first */
#include <Python.h>

#include <glib.h>
#include <glib/gstdio.h>
#include "cards.h"
#include "cfg.h"

Config cfg;

/* 
 * create a new $XDG_CONFIG_HOME/gnome-hearts/gnome-hearts.cfg file
 *
 * If an old configuration file exists at $HOME/.gnome-hearts.cfg it will
 * copy that and then delete it.
 */
static void config_create(void)
{
	gchar *buffer;
	gsize size;

	gchar *old_file = g_build_filename(g_get_home_dir(), "/.gnome-hearts.cfg", NULL);
	gchar *new_file = g_build_filename(PACKAGE_DATA_DIR, "gnome-hearts", "gnome-hearts.cfg", NULL);

	if (!g_file_test(cfg.config_path, G_FILE_TEST_EXISTS))
		g_mkdir_with_parents(cfg.config_path, 0700);

	if (g_file_test(old_file, G_FILE_TEST_EXISTS))
	{
		g_file_get_contents(old_file, &buffer, &size, NULL);
		g_file_set_contents(cfg.config_file, buffer, size, NULL);
		g_unlink(old_file);
	}
	else
	{
		g_file_get_contents(new_file, &buffer, &size, NULL);
		g_file_set_contents(cfg.config_file, buffer, size, NULL);
	}

	g_free(old_file);
	g_free(new_file);
	g_free(buffer);
}

/* Load a configuration from a keyfile pointer */
static void config_load_from_keyfile(GKeyFile *file)
{
	gchar *ruleset = g_key_file_get_string(file, "hearts", "ruleset", NULL);
	if (g_ascii_strcasecmp(ruleset, "standard") == 0) cfg.ruleset = RULESET_STANDARD;
	if (g_ascii_strcasecmp(ruleset, "omnibus") == 0) cfg.ruleset = RULESET_OMNIBUS;
	if (g_ascii_strcasecmp(ruleset, "omnibus_alt") == 0) cfg.ruleset = RULESET_OMNIBUS_ALT;
	if (g_ascii_strcasecmp(ruleset, "spot_hearts") == 0) cfg.ruleset = RULESET_SPOT_HEARTS;
	g_free(ruleset);

	cfg.clubs_lead = g_key_file_get_boolean(file, "hearts", "clubs_lead", NULL);
	cfg.hearts_break = g_key_file_get_boolean(file, "hearts", "hearts_break", NULL);
	cfg.no_blood = g_key_file_get_boolean(file, "hearts", "no_blood", NULL);
	cfg.queen_breaks_hearts = g_key_file_get_boolean(file, "hearts", "queen_breaks_hearts", NULL);
	cfg.show_scores = g_key_file_get_boolean(file, "hearts", "show_scores", NULL);
	
	cfg.north_ai = g_key_file_get_string(file, "hearts", "north_ai", NULL);
	cfg.east_ai = g_key_file_get_string(file, "hearts", "east_ai", NULL);
	cfg.west_ai = g_key_file_get_string(file, "hearts", "west_ai", NULL);
	
	cfg.card_style = g_key_file_get_string(file, "hearts", "card_style", NULL);
	cfg.background_image = g_key_file_get_string(file, "hearts", "background_image", NULL);
	cfg.background_tiled = g_key_file_get_boolean(file, "hearts", "background_tiled", NULL);
}

/* Load the gnome-hearts configuration */
void config_load(void)
{
	GKeyFile *file = g_key_file_new();
	
	cfg.config_path = (g_getenv("XDG_CONFIG_HOME") == NULL
			? g_build_filename(g_get_home_dir(), ".config", "gnome-hearts", NULL)
			: g_strdup(g_getenv("XDG_CONFIG_HOME")));
	cfg.config_file = g_build_filename(cfg.config_path, "gnome-hearts.cfg", NULL);

	if (!g_file_test(cfg.config_file, G_FILE_TEST_EXISTS))
		config_create();

	g_key_file_load_from_file(file, cfg.config_file, G_KEY_FILE_KEEP_COMMENTS, NULL);

	/* replace ~/.gnome-hearts.cfg if it's outdated. Increment this everytime the config changes */
	gint version = g_key_file_get_integer(file, "hearts", "version", NULL);
	if (version < 3)
	{
		config_create();
		g_key_file_load_from_file(file, cfg.config_file, G_KEY_FILE_KEEP_COMMENTS, NULL);
	}
	
	config_load_from_keyfile(file);
	g_key_file_free(file);

	/* Update the configuration in Python */
	config_publish();
}

/* Save the gnome-hearts configuration */
void config_save(void)
{
	gsize size;
	GKeyFile *file = g_key_file_new();
	g_key_file_load_from_file(file, cfg.config_file, G_KEY_FILE_KEEP_COMMENTS, NULL);
	
	gchar *ruleset;
	switch (cfg.ruleset)
	{
		case RULESET_OMNIBUS: ruleset = "omnibus"; break;
		case RULESET_OMNIBUS_ALT: ruleset = "omnibus_alt"; break;
		case RULESET_SPOT_HEARTS: ruleset = "spot_hearts"; break;
		case RULESET_STANDARD: default: ruleset = "standard"; break;

	}
	g_key_file_set_string(file, "hearts", "ruleset", ruleset);
	
	g_key_file_set_boolean(file, "hearts", "clubs_lead", cfg.clubs_lead);
	g_key_file_set_boolean(file, "hearts", "hearts_break", cfg.hearts_break);
	g_key_file_set_boolean(file, "hearts", "no_blood", cfg.no_blood);
	g_key_file_set_boolean(file, "hearts", "queen_breaks_hearts", cfg.queen_breaks_hearts);
	g_key_file_set_boolean(file, "hearts", "show_scores", cfg.show_scores);
	
	g_key_file_set_string(file, "hearts", "north_ai", cfg.north_ai);
	g_key_file_set_string(file, "hearts", "east_ai", cfg.east_ai);
	g_key_file_set_string(file, "hearts", "west_ai", cfg.west_ai);

	g_key_file_set_string(file, "hearts", "card_style", cfg.card_style);
	g_key_file_set_string(file, "hearts", "background_image", cfg.background_image);
	g_key_file_set_boolean(file, "hearts", "background_tiled", cfg.background_tiled);
	
	gchar *buffer = g_key_file_to_data(file, &size, NULL);
	g_key_file_free(file);
	
	/* write it to the cfg file */
	g_file_set_contents(cfg.config_file, buffer, size, NULL);
	g_free(buffer);
}

/* Publish the config to Python */
void config_publish(void)
{
	gchar *ruleset;
	PyObject *module, *dict, *object, *result;
	
	/* Get a reference to score.set() */
	module = PyImport_AddModule("__main__");
	dict = PyModule_GetDict(module);
	object = PyDict_GetItemString(dict, "rules");

	switch (cfg.ruleset)
	{
		case RULESET_OMNIBUS: ruleset = "omnibus"; break;
		case RULESET_OMNIBUS_ALT: ruleset = "omnibus_alt"; break;
		case RULESET_SPOT_HEARTS: ruleset = "spot_hearts"; break;
		case RULESET_STANDARD: default: ruleset = "standard"; break;

	}

	result = PyObject_CallMethod(object, "set", "siiii", ruleset, cfg.clubs_lead, cfg.hearts_break, cfg.queen_breaks_hearts, cfg.no_blood);

	Py_DECREF(result);
}

/* Free the allocated data */
void config_free(void)
{
	g_free(cfg.north_ai);
	g_free(cfg.east_ai);
	g_free(cfg.west_ai);
	g_free(cfg.card_style);
	g_free(cfg.background_image);
	g_free(cfg.config_path);
	g_free(cfg.config_file);
}

