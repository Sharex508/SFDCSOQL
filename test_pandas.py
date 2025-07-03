import pandas as pd
import sys

def test_pandas():
    """Test that pandas is installed and working correctly."""
    print(f"Pandas version: {pd.__version__}")
    
    # Create a simple DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    
    print("\nSample DataFrame:")
    print(df)
    
    print("\nPandas is installed and working correctly!")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    test_pandas()