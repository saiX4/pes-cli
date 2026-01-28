#!/usr/bin/env python3
"""
Examples of auto-selecting all options in inquirer when one specific option is selected.
"""

import inquirer
from inquirer import events

# ============================================================================
# METHOD 1: Using a "Select All" option with custom validation
# ============================================================================

def method1_select_all_option():
    """
    Add a 'Select All' option that when chosen, selects everything.
    """
    choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    
    questions = [
        inquirer.Checkbox(
            'items',
            message="Select items (choose 'Select All' to select everything)",
            choices=['[Select All]'] + choices,
        ),
    ]
    
    answers = inquirer.prompt(questions)
    
    # If "Select All" was chosen, return all options
    if '[Select All]' in answers['items']:
        selected = choices  # All actual choices (excluding the Select All option)
    else:
        selected = answers['items']
    
    print(f"\nSelected items: {selected}")
    return selected


# ============================================================================
# METHOD 2: Post-processing with a trigger option
# ============================================================================

def method2_trigger_option():
    """
    If a specific option is selected, automatically add all others.
    """
    choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    trigger = 'Select All'
    
    questions = [
        inquirer.Checkbox(
            'items',
            message="Select items",
            choices=[trigger] + choices,
        ),
    ]
    
    answers = inquirer.prompt(questions)
    selected = answers['items']
    
    # If trigger option is selected, add all other options
    if trigger in selected:
        selected = choices  # Replace with all choices (excluding trigger)
    
    print(f"\nSelected items: {selected}")
    return selected


# ============================================================================
# METHOD 3: Using custom event handling (Advanced)
# ============================================================================

def method3_custom_event_handler():
    """
    Use custom key bindings to select all with a keyboard shortcut.
    This is more advanced and works during the prompt.
    """
    from inquirer.render.console import ConsoleRender
    from inquirer.render.console._checkbox import Checkbox as CheckboxRender
    
    choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    
    # Create a custom render that handles Ctrl+A to select all
    class CustomCheckboxRender(CheckboxRender):
        def handle_keypress(self, event):
            # Ctrl+A to select all
            if event.key == 'c-a':
                # Select all options
                self.question.answers = list(self.question.choices)
                self.current = self.question.choices[0]
            else:
                super().handle_keypress(event)
    
    questions = [
        inquirer.Checkbox(
            'items',
            message="Select items (Press Ctrl+A to select all)",
            choices=choices,
        ),
    ]
    
    # Note: Custom render classes require more setup
    # This is a simplified example
    print("\nNote: Method 3 requires custom implementation.")
    print("Use Method 1 or 2 for simpler solutions.\n")


# ============================================================================
# METHOD 4: Two-step process (recommended for clarity)
# ============================================================================

def method4_two_step():
    """
    Ask first if user wants to select all, then show checkbox if needed.
    """
    choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    
    questions = [
        inquirer.List(
            'select_all',
            message="Do you want to select all items?",
            choices=['Yes, select all', 'No, let me choose'],
        ),
    ]
    
    answer = inquirer.prompt(questions)
    
    if answer['select_all'] == 'Yes, select all':
        selected = choices
        print(f"\nAll items selected: {selected}")
    else:
        questions = [
            inquirer.Checkbox(
                'items',
                message="Select items",
                choices=choices,
            ),
        ]
        answer = inquirer.prompt(questions)
        selected = answer['items']
        print(f"\nSelected items: {selected}")
    
    return selected


# ============================================================================
# METHOD 5: Default all selected (user deselects what they don't want)
# ============================================================================

def method5_default_all_selected():
    """
    Start with all options selected by default.
    """
    choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    
    questions = [
        inquirer.Checkbox(
            'items',
            message="Deselect items you don't want (all selected by default)",
            choices=choices,
            default=choices,  # All selected by default
        ),
    ]
    
    answers = inquirer.prompt(questions)
    selected = answers['items']
    
    print(f"\nSelected items: {selected}")
    return selected


# ============================================================================
# METHOD 6: Detect specific option and auto-complete
# ============================================================================

def method6_detect_and_autocomplete():
    """
    When a specific option like "All" is detected in the selection,
    automatically add all other options.
    """
    all_choices = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
    choices_with_trigger = ['ALL'] + all_choices
    
    questions = [
        inquirer.Checkbox(
            'items',
            message="Select items (selecting 'ALL' will select everything)",
            choices=choices_with_trigger,
        ),
    ]
    
    answers = inquirer.prompt(questions)
    selected = answers['items']
    
    # Check if 'ALL' is in the selection
    if 'ALL' in selected:
        # Return all actual options (not including 'ALL')
        selected = all_choices
        print(f"\n'ALL' detected - all items selected: {selected}")
    else:
        print(f"\nSelected items: {selected}")
    
    return selected


# ============================================================================
# MAIN - Demo all methods
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INQUIRER AUTO-SELECT EXAMPLES")
    print("=" * 70)
    
    while True:
        print("\nChoose a method to demo:")
        print("1. Method 1: Select All option (simple)")
        print("2. Method 2: Trigger option with post-processing")
        print("3. Method 3: Custom event handler (advanced - info only)")
        print("4. Method 4: Two-step process (recommended)")
        print("5. Method 5: Default all selected (user deselects)")
        print("6. Method 6: Detect and auto-complete")
        print("0. Exit")
        
        choice_questions = [
            inquirer.List(
                'method',
                message="Select method",
                choices=[
                    '1 - Select All option',
                    '2 - Trigger option',
                    '3 - Custom event handler (info)',
                    '4 - Two-step process',
                    '5 - Default all selected',
                    '6 - Detect and auto-complete',
                    '0 - Exit'
                ],
            ),
        ]
        
        choice = inquirer.prompt(choice_questions)
        method = choice['method'][0]  # Get first character
        
        print("\n" + "=" * 70)
        
        if method == '1':
            print("METHOD 1: Select All Option\n")
            method1_select_all_option()
        elif method == '2':
            print("METHOD 2: Trigger Option\n")
            method2_trigger_option()
        elif method == '3':
            print("METHOD 3: Custom Event Handler\n")
            method3_custom_event_handler()
        elif method == '4':
            print("METHOD 4: Two-Step Process\n")
            method4_two_step()
        elif method == '5':
            print("METHOD 5: Default All Selected\n")
            method5_default_all_selected()
        elif method == '6':
            print("METHOD 6: Detect and Auto-complete\n")
            method6_detect_and_autocomplete()
        elif method == '0':
            print("Exiting...")
            break
        
        print("=" * 70)
        
        continue_q = [
            inquirer.Confirm(
                'continue',
                message="Try another method?",
                default=True,
            ),
        ]
        
        if not inquirer.prompt(continue_q)['continue']:
            break
    
    print("\nDone!")