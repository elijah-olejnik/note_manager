import gettext
import sys

_ = gettext.gettext


def set_language(lang_code):
    try:
        lang = gettext.translation('messages', localedir='locales', languages=[lang_code])
        lang.install()
        global _
        _ = lang.gettext
    except FileNotFoundError:
        print(f"Sorry, language {lang_code} is not supported.")
        sys.exit(1)


# Exception messages
missing_fields_str = _("Missing required fields in record: ")
data_fmt_err_str = _("Data format error in record ")
empty_list_io_str = _("File IO function returned empty list.")
import_failed_str = _("Failed to import notes: ")
note_with_id_str = _("Note with ID ")
not_found_str = _(" not found.")
file_str = _("File ")
is_empty_str = _(" is empty!")
yaml_import_failed_str = _("Import from YAML file failed: ")
json_import_failed_str = _("Import from JSON file failed: ")
yaml_export_failed_str = _("Export to YAML file failed: ")
json_export_failed_str = _("Export to JSON file failed: ")
empty_list_export_str = _("You're trying to export an empty list.")
deadline_invalid_str = _("The deadline can be only in the future.")
enum_error_str = _("Not an Enum value: ")

# Warnings messages
new_file_str = _("A new file is created.")
new_file_failed_str = _("Can't create a new file: ")
note_list_empty_str = _("The note list is empty.")

# CLI strings
no_deadline_str = _("NO DEADLINE")
femto_str = _("Edit your note text. To exit and save text press Esc.")
welcome_str = _("Welcome to the note manager!")
note_id_str = _("Note ID")
username_str = _("Username")
title_str = _("Title")
content_str = _("Content")
status_str = _("Status")
created_date_str = _("Created date")
issue_date_str = _("Deadline date")
k_wds_str = _("Keywords")
both_str = _("Both")
confirmation_message_str = _("Are you sure? yes | no: ")
no_notes_disp_str = _("No notes to display.")
no_notes_found_str = _("No notes found.")
page_str = _("Page")
total_str = _("total")
next_pg_str = _("next page")
prev_pg_str = _("previous page")
quit_str = _("quit")
last_pg_str = _("You are on the last page.")
first_pg_str = _("You are on the first page.")
invalid_choice_str = _("Invalid choice.")
correct_cmds_str = _("The correct commands are")
note_created_str = _("The note created:")
note_chosen_str = _("The note chosen:")
note_updated_str = _("The note updated:")
note_str = _("The note")
del_str = _("deleted")
search_str = _("Search")
search_by_str = _("Search by")
show_all_str = _("Show all")
no_matches_fnd_str = _("No matches found.")
choose_note_str = _("Choose a note")
del_note_str = _("Delete a note")
or_str = _("or")
choose_state_str = _("Choose the new note state")
note_disp_ops = _("Notes display options")
show_str = _("Show notes")
sort_str = _("Sort notes")
full_str = _("full")
short_str = _("shortened")
asc_str = _("Ascending")
desc_str = _("descending")
edit_menu_str = _("Note edit menu")
back_str = _("Back to the main menu")
main_menu_str = _("Main menu")
create_note_str = _("Create a note")
upd_note_str = _("Edit a note")
missed_str = _("Missing deadline:")
today_str = _("The deadline is today:")
tomorrow_str = _("The deadline is tomorrow:")

# CLI prompts
enter_choice_str = _("Enter choice: ")
enter_username_str = _("Enter a username: ")
enter_title_str = _("Enter a title: ")
enter_issue_str = _("Enter note deadline (dd-mm-yyyy hh:mm): ")
enter_k_wds_str = _("Enter keywords, separated by ")
enter_disp_ops_str = _("Enter display options, only 3 supported\n"
                       "(e.g. for show note in full sorting by created date ascending enter")