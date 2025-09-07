#!/usr/bin/env python3
"""
Big CSV File Splitter
Splits large CSV files into smaller chunks while preserving headers
Each chunk file is named: chunk_1.csv, chunk_2.csv, etc.
"""

import pandas as pd
import os
import sys
from pathlib import Path
from tqdm import tqdm
import argparse

def split_csv_file(input_file, chunk_size=10000, output_dir="chunks", prefix="chunk"):
    """
    Split a large CSV file into smaller chunks with headers
    
    Args:
        input_file (str): Path to the input CSV file
        chunk_size (int): Number of rows per chunk (default: 10000)
        output_dir (str): Directory to save chunks (default: "chunks")
        prefix (str): Prefix for chunk filenames (default: "chunk")
    
    Returns:
        dict: Summary of the split operation
    """
    
    print("📁 BIG CSV FILE SPLITTER")
    print("=" * 30)
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found!")
        return None
    
    # Get file info
    file_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
    print(f"📊 Input file: {input_file}")
    print(f"📏 File size: {file_size:.2f} MB")
    print(f"📦 Chunk size: {chunk_size:,} rows per file")
    print(f"📁 Output directory: {output_dir}")
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    print(f"✅ Created/verified directory: {output_dir}")
    
    try:
        # First, count total rows for progress bar
        print("\n🔍 Analyzing file structure...")
        total_rows = sum(1 for _ in open(input_file)) - 1  # Subtract header
        total_chunks = (total_rows + chunk_size - 1) // chunk_size  # Ceiling division
        
        print(f"📊 Total data rows: {total_rows:,}")
        print(f"📦 Expected chunks: {total_chunks}")
        
        # Read and split the CSV file
        print("\n⚡ Processing chunks...")
        
        chunk_info = []
        
        # Use tqdm for progress tracking
        chunk_iterator = pd.read_csv(input_file, chunksize=chunk_size)
        
        for i, chunk in enumerate(tqdm(chunk_iterator, total=total_chunks, desc="Splitting")):
            chunk_filename = f"{prefix}_{i + 1:03d}.csv"  # Zero-padded numbering
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            # Save chunk with headers
            chunk.to_csv(chunk_path, index=False)
            
            # Store chunk info
            chunk_info.append({
                'chunk_number': i + 1,
                'filename': chunk_filename,
                'rows': len(chunk),
                'size_mb': os.path.getsize(chunk_path) / (1024 * 1024)
            })
        
        # Summary
        total_output_size = sum(info['size_mb'] for info in chunk_info)
        
        print("\n✅ SPLIT COMPLETE!")
        print(f"📦 Created {len(chunk_info)} chunk files")
        print(f"📏 Total output size: {total_output_size:.2f} MB")
        print(f"📁 Files saved in: {output_dir}/")
        
        # Show chunk details
        print("\n📋 CHUNK DETAILS:")
        for info in chunk_info[:5]:  # Show first 5 chunks
            print(f"   📄 {info['filename']}: {info['rows']:,} rows ({info['size_mb']:.2f} MB)")
        
        if len(chunk_info) > 5:
            print(f"   📄 ... and {len(chunk_info) - 5} more files")
        
        return {
            'input_file': input_file,
            'total_chunks': len(chunk_info),
            'total_rows': total_rows,
            'chunk_size': chunk_size,
            'output_dir': output_dir,
            'chunks': chunk_info
        }
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def list_csv_files():
    """List available CSV files in the current directory"""
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if csv_files:
        print("\n📁 Available CSV files in current directory:")
        for i, file in enumerate(csv_files, 1):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print(f"   {i}. {file} ({size_mb:.2f} MB)")
        return csv_files
    else:
        print("\n📁 No CSV files found in current directory")
        return []

def interactive_mode():
    """Interactive mode for user-friendly file selection"""
    print("🔄 INTERACTIVE MODE")
    print("=" * 20)
    
    # List available files
    csv_files = list_csv_files()
    
    if not csv_files:
        print("❌ No CSV files found. Please add a CSV file to the current directory.")
        return
    
    # Let user select file
    while True:
        try:
            choice = input(f"\nSelect a file (1-{len(csv_files)}) or enter filename: ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(csv_files):
                    input_file = csv_files[index]
                    break
                else:
                    print(f"❌ Invalid choice. Please select 1-{len(csv_files)}")
            else:
                if os.path.exists(choice):
                    input_file = choice
                    break
                else:
                    print(f"❌ File '{choice}' not found")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return
    
    # Get chunk size
    while True:
        try:
            chunk_input = input("\nChunk size (rows per file) [default: 10000]: ").strip()
            if not chunk_input:
                chunk_size = 10000
                break
            else:
                chunk_size = int(chunk_input)
                if chunk_size > 0:
                    break
                else:
                    print("❌ Chunk size must be positive")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return
    
    # Get output directory
    output_dir = input("\nOutput directory [default: chunks]: ").strip()
    if not output_dir:
        output_dir = "chunks"
    
    # Confirm operation
    print("\n📋 OPERATION SUMMARY:")
    print(f"   📄 Input file: {input_file}")
    print(f"   📦 Chunk size: {chunk_size:,} rows")
    print(f"   📁 Output directory: {output_dir}")
    
    confirm = input("\nProceed? (y/N): ").strip().lower()
    if confirm == 'y':
        result = split_csv_file(input_file, chunk_size, output_dir)
        if result:
            print("\n🎉 Operation completed successfully!")
    else:
        print("❌ Operation cancelled")

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Split large CSV files into smaller chunks')
    parser.add_argument('input_file', nargs='?', help='Input CSV file path')
    parser.add_argument('--chunk-size', '-c', type=int, default=10000, 
                       help='Number of rows per chunk (default: 10000)')
    parser.add_argument('--output-dir', '-o', default='chunks', 
                       help='Output directory (default: chunks)')
    parser.add_argument('--prefix', '-p', default='chunk', 
                       help='Filename prefix (default: chunk)')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not args.input_file:
        interactive_mode()
    else:
        result = split_csv_file(args.input_file, args.chunk_size, args.output_dir, args.prefix)
        if result:
            print(f"\n🎉 Successfully split {args.input_file} into {result['total_chunks']} chunks!")

# Quick test with your existing file
def quick_split():
    """Quick split function for testing"""
    # Look for the most recent export file
    csv_files = [f for f in os.listdir('.') if f.startswith('complete_sales_data_') and f.endswith('.csv')]
    
    if csv_files:
        # Get the most recent file
        latest_file = max(csv_files, key=os.path.getctime)
        print(f"🔍 Found recent export: {latest_file}")
        
        # Split it
        result = split_csv_file(latest_file, chunk_size=50000, output_dir="sales_chunks")
        return result
    else:
        print("❌ No sales data export files found")
        print("💡 Try running the retail menu first (Option 6 - Export Data)")
        return None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, try quick split first
        print("🚀 QUICK SPLIT MODE")
        print("=" * 20)
        result = quick_split()
        
        if not result:
            print("\n🔄 Switching to interactive mode...")
            interactive_mode()
    else:
        main()
   