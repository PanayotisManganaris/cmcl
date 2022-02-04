import click

def cli():
    pass
    
@click.command()
def gather():
    """Crawls directories for DFT inputs/outputs and makes a dataframe out of them"""
    pymatgen.borg.assimiliation()
    jiaqi.help.here()
    
@click.command()
def predict(formula: str):
    if valid_str(formula):
        features = featurize(formula)
        matprop = fit(features)
        return matprop
    else:
        print("invalid formula")
        
if __name__ = "__main__":
    cli()
