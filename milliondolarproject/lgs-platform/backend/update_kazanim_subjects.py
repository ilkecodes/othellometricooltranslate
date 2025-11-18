#!/usr/bin/env python3
"""
Kazanım Subject Updater: Fix unknown English kazanımlar

Updates kazanımlar that should be classified as English based on content analysis.
"""

import json
import sys

def update_kazanim_subjects(input_file: str, output_file: str):
    """Update unknown kazanımlar with proper subject classification."""
    
    updated_count = 0
    total_count = 0
    
    print("📝 Updating kazanım subjects...")
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                try:
                    kazanim = json.loads(line)
                    total_count += 1
                    
                    # Check if this should be classified as English
                    subject = kazanim.get('subject')
                    code = kazanim.get('code', '')
                    description = kazanim.get('description', '').lower()
                    
                    if not subject or subject == 'Unknown':
                        # English indicators
                        is_english = (
                            any(word in description for word in [
                                'student', 'teacher', 'lesson', 'vocabulary', 'grammar', 
                                'speaking', 'listening', 'reading', 'writing', 'warm-up',
                                'icebreaker', 'class', 'activity', 'story', 'digital story',
                                'board', 'volunteers', 'picture', 'target words'
                            ]) or
                            any(code.startswith(prefix) for prefix in [
                                'D1', 'D2', 'D3', 'V3', 'V4', 'V6', 'V7', 'V12', 'V13', 
                                'V14', 'V19', 'V20', 'LS', 'CS2', 'CS3', 'SELS1', 'SELS2', 'SELS3'
                            ])
                        )
                        
                        if is_english:
                            kazanim['subject'] = 'English'
                            updated_count += 1
                            print(f"  ✓ Updated {code}: {description[:50]}...")
                        else:
                            print(f"  ⚠️ Keeping unknown: {code}: {description[:50]}...")
                    
                    # Write the (possibly updated) kazanım
                    outfile.write(json.dumps(kazanim, ensure_ascii=False) + '\n')
                    
                except Exception as e:
                    print(f"  ✗ Error on line {line_num}: {e}")
    
    print(f"\\n✅ Updated {updated_count} out of {total_count} kazanımlar")
    print(f"📁 Output saved to: {output_file}")

def main():
    """Main function."""
    
    if len(sys.argv) != 3:
        print("Usage: python update_kazanim_subjects.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        update_kazanim_subjects(input_file, output_file)
        
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()