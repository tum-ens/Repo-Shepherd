History Commit Message Refinement
==================

Introduction
------------

This section introduces the History Commit Message Refinement function in **Commit Analyzer** tab.

.. image:: ../image/usage/CM_history.png

Left Frame: Setup Buttons
-------------------------

**Branch**: Select the branch whose commit history you want to refine.

**Commit Messages**: Choose how many commit messages to refine.  
You can select **latest**, **oldest**, or **all**.

Left Frame: Function Buttons
----------------------------

**Fetch**: Fetches commit history based on your selections.

**Refine All**: Refines all the listed commit messages.  
Merge commits will be skipped.  
The processing time depends on the number of messages and the LLM's RPM (requests per minute) limits.

**Push**: Pushes the refined commit messages to the remote repository, replacing the original messages.

Left Frame: Navigation Buttons
------------------------------

**Help**: Displays simple instructions for using this tab.

**Back**: Returns to the main tab.

Right Frame: Commit Message List
--------------------------------

This frame displays the commits based on your selection.  
You can click on a commit to refine it individually.

.. image:: ../image/usage/CM_detail.png

- The left panel shows the **original commit message**.  
- The right panel shows the **refined commit message**.

**Code Diff**: Displays the code diff for the selected commit.

**Refine**: Generates a refined commit message based on the original message and code diff.  
You can also manually edit the refined message.

**Clear**: Clears the refined message.

**Save**: Saves the refined message.