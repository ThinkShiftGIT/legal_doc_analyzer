from pathlib import Path
from legal_doc_analyzer.utils.project_summary import ProjectSummarizer

def main():
    # Get the project root directory
    project_root = Path(__file__).parent

    # Create summarizer
    summarizer = ProjectSummarizer(project_root)
    
    # Generate summary
    summary = summarizer.generate_summary()
    
    # Save to file
    output_file = project_root / "PROJECT_SUMMARY.md"
    with open(output_file, "w") as f:
        f.write(summary)
        
    print(f"Summary has been saved to: {output_file.absolute()}")

if __name__ == "__main__":
    main()