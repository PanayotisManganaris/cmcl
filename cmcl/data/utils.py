def match_labels(p_cols, e_cols):
    matched = []
    for e_col in e_cols:
        for p_col in p_cols:
            if p_col[2::] == e_col:
                matched.append(e_col)
                matched.append(p_col)
    return matched
        

def pvse(df):
    allcol = df.columns.to_list()
    p_cols = [col for col in allcol if "p_" in col]
    e_cols = [col for col in allcol if "p_" not in col]
    match = match_labels(p_cols, e_cols)
    pvse_df = df[match]
    return pvse_df

def makegrid(df):
    plotl = df.columns.to_list()
    nplot = len(plotl)
    #aim for 3 for now
    if nplot / 3 <= 1:
        ncol = nplot
        nrow = 1
    else:
        ncol = (nplot - (nplot % 3))/3
        nrow = ncol+1
    return [int(ncol), int(nrow)]
