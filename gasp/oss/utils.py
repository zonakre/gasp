"""
Manage data in folders
"""

def identify_groups(folder, splitStr, groupPos, outFolder):
    """
    Identifica o grupo a que um ficheiro pertence e envia-o para uma nova
    pasta com os ficheiros que pertencem a esse grupo.
    
    Como e que o grupo e identificado?
    * O nome do ficheiro e partido em dois em funcao de splitStr;
    * O groupPos identifica qual e a parte (primeira ou segunda) que 
    corresponde ao grupo.
    """
    
    import os
    
    from gasp.oss     import list_files
    from gasp.oss.ops import create_folder
    from gasp.oss.ops import copy_file
    
    files = list_files(folder)
    
    # List groups and relate files with groups:
    groups = {}
    for _file in files:
        # Split filename
        filename = os.path.splitext(os.path.basename(_file))[0]
        fileForm = os.path.splitext(os.path.basename(_file))[1]
        group = filename.split(splitStr)[groupPos]
        namePos = 1 if not groupPos else 0
        
        if group not in groups:
            groups[group] = [[filename.split(splitStr)[namePos], fileForm]]
        else:
            groups[group].append([filename.split(splitStr)[namePos], fileForm])
    
    # Create one folder for each group and put there the files related
    # with that group.
    for group in groups:
        group_folder = create_folder(os.path.join(outFolder, group))
            
        for filename in groups[group]:
            copy_file(
                os.path.join(folder, '{a}{b}{c}{d}'.format(
                    a=filename[0], b=splitStr, c=group,
                    d=filename[1]
                )),
                os.path.join(group_folder, '{a}{b}'.format(
                    a=filename[0], b=filename[1]
                ))
            )

