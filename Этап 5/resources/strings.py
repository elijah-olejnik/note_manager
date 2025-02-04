from .localization import _, language_manager


class StringsProvider:
    """Class StringsProvider stores all user-readable strings
    and handles their translations the other languages.
    """
    def __init__(self):
        # Exception messages
        self.missing_fields_str = _("Missing required fields in record: ")
        self.data_fmt_err_str = _("Data format error in record ")
        self.empty_list_io_str = _("File IO function returned empty list.")
        self.import_failed_str = _("Failed to import notes: ")
        self.note_with_id_str = _("Note with ID ")
        self.not_found_str = _(" not found.")
        self.file_str = _("File ")
        self.is_empty_str = _(" is empty!")
        self.yaml_import_failed_str = _("Import from YAML file failed: ")
        self.json_import_failed_str = _("Import from JSON file failed: ")
        self.yaml_export_failed_str = _("Export to YAML file failed: ")
        self.json_export_failed_str = _("Export to JSON file failed: ")
        self.empty_list_export_str = _("You're trying to export an empty list.")
        self.deadline_invalid_str = _("The deadline can be only in the future.")
        self.enum_error_str = _("Not an Enum value: ")

        # Warnings messages
        self.new_file_str = _("A new file is created.")
        self.new_file_failed_str = _("Can't create a new file: ")
        self.note_list_empty_str = _("The note list is empty.")

        # CLI strings
        self.no_deadline_str = _("NO DEADLINE")
        self.femto_str = _("Edit your note text. To exit and save text press Esc.")
        self.welcome_str = _("Welcome to the note manager!")
        self.note_id_str = _("Note ID")
        self.username_str = _("Username")
        self.title_str = _("Title")
        self.content_str = _("Content")
        self.status_str = _("Status")
        self.created_date_str = _("Created date")
        self.issue_date_str = _("Deadline date")
        self.k_wds_str = _("Keywords")
        self.both_str = _("Both")
        self.confirmation_message_str = _("Are you sure? yes | no: ")
        self.no_notes_disp_str = _("No notes to display.")
        self.no_notes_found_str = _("No notes found.")
        self.page_str = _("Page")
        self.total_str = _("total")
        self.next_pg_str = _("next page")
        self.prev_pg_str = _("previous page")
        self.quit_str = _("quit")
        self.last_pg_str = _("You are on the last page.")
        self.first_pg_str = _("You are on the first page.")
        self.invalid_choice_str = _("Invalid choice.")
        self.correct_cmds_str = _("The correct commands are")
        self.note_created_str = _("The note created:")
        self.note_chosen_str = _("The note chosen:")
        self.note_updated_str = _("The note updated:")
        self.note_str = _("The note")
        self.del_str = _("deleted")
        self.search_str = _("Search")
        self.search_by_str = _("Search by")
        self.show_all_str = _("Show all")
        self.no_matches_fnd_str = _("No matches found.")
        self.choose_note_str = _("Choose a note")
        self.del_note_str = _("Delete a note")
        self.or_str = _("or")
        self.choose_state_str = _("Choose the new note state")
        self.note_disp_ops = _("Notes display options")
        self.show_str = _("Show notes")
        self.sort_str = _("Sort notes")
        self.full_str = _("full")
        self.short_str = _("shortened")
        self.asc_str = _("Ascending")
        self.desc_str = _("descending")
        self.edit_menu_str = _("Note edit menu")
        self.back_str = _("Back to the main menu")
        self.main_menu_str = _("Main menu")
        self.create_note_str = _("Create a note")
        self.upd_note_str = _("Edit a note")
        self.missed_str = _("Missing deadline:")
        self.today_str = _("The deadline is today:")
        self.tomorrow_str = _("The deadline is tomorrow:")

        # CLI prompts
        self.enter_choice_str = _("Enter choice: ")
        self.enter_username_str = _("Enter a username: ")
        self.enter_title_str = _("Enter a title: ")
        self.enter_issue_str = _("Enter note deadline (dd-mm-yyyy hh:mm): ")
        self.enter_k_wds_str = _("Enter keywords, separated by ")
        self.enter_disp_ops_str = _("Enter display options, only 3 supported\n"
                               "(e.g. for show note in full sorting by created date ascending enter")

    def change_language(self, lang_code):
        """The function changes strings language to a given one."""
        language_manager.set_locale(lang_code)
        self.__init__()


strings = StringsProvider()
