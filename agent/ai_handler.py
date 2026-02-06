
import requests
import json
import logging

class AIHandler:
    def __init__(self, secrets, resume_text=""):
        self.logger = logging.getLogger("AutoJobApplier.AI")
        self.base_url = secrets['ollama']['base_url']
        self.model = secrets['ollama']['model']
        self.resume_text = resume_text

    def generate_answer(self, question, field_type="text", job_description=""):
        """
        Generates an answer to a specific question using Ollama.
        """
        
        # Extract specific information from resume for common fields
        question_lower = question.lower()
        
        # Handle phone number specifically
        if 'phone' in question_lower or 'mobile' in question_lower:
            import re
            # Look for phone numbers in resume
            phone_patterns = [
                r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})',  # (555) 123-4567
                r'(\d{10})',  # 5551234567
                r'Phone:\s*([+\d\s()-]+)',
                r'Mobile:\s*([+\d\s()-]+)'
            ]
            for pattern in phone_patterns:
                match = re.search(pattern, self.resume_text)
                if match:
                    phone = ''.join(filter(str.isdigit, match.group(0)))[-10:]  # Last 10 digits
                    self.logger.info(f"[numeric] Q: {question} | A: {phone}")
                    return phone
        
        # Handle city specifically
        if 'city' in question_lower and 'city' not in question_lower.replace('city', ''):
            import re
            city_patterns = [
                r'City:\s*([A-Za-z\s]+)',
                r'Location:\s*([A-Za-z\s]+),',
                r'([A-Za-z\s]+),\s*[A-Z]{2}'  # City, ST format
            ]
            for pattern in city_patterns:
                match = re.search(pattern, self.resume_text)
                if match:
                    city = match.group(1).strip()
                    self.logger.info(f"[text] Q: {question} | A: {city}")
                    return city
        
        # Specialized rule for known field types
        rule = ""
        if field_type == "numeric":
            rule = "Output ONLY a number. No text, no labels, just the number."
        elif field_type == "boolean":
            rule = "Output ONLY 'Yes' or 'No'."
        
        prompt = f"""
        You are an assistant filling out a job application.
        
        My Info:
        {self.resume_text[:2000]}
        
        The Question: "{question}"
        Field Type: {field_type}
        
        Instructions:
        - Answer based ONLY on the resume information above.
        - {rule}
        - If asked for phone/mobile, output ONLY digits (e.g., 5551234567).
        - If asked for city, output ONLY the city name.
        - If asked for years of experience, output ONLY the number.
        - Keep it purely the answer value, nothing else.
        
        Answer:
        """

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            answer = result['response'].strip()
            
            # Clean up answer - remove newlines and extra whitespace
            answer = answer.replace('\n', ' ').replace('\r', ' ')
            answer = ' '.join(answer.split())  # Normalize whitespace
            
            # CRITICAL: Clean numeric responses (e.g., "3.5/4.0" → "3.5")
            answer = self._clean_numeric_answer(answer, question, field_type)
            
            # Post-processing cleanups
            if field_type == "numeric":
                import re
                digits = re.findall(r'\d+', answer)
                if digits: answer = digits[0]
            
            self.logger.info(f"[{field_type}] Q: {question[:60]} | A: {answer}")
            return answer

        except Exception as e:
            self.logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _clean_numeric_answer(self, answer, question, field_type):
        """Clean numeric answers to extract just the number."""
        if not answer:
            return answer
        
        import re
        
        question_lower = question.lower()
        
        # Check if this is a numeric field that needs cleaning
        numeric_keywords = ['cgpa', 'gpa', 'scale', 'score', 'percentage', '%', 'years', 'salary']
        is_numeric_question = any(kw in question_lower for kw in numeric_keywords) or field_type == 'numeric'
        
        if not is_numeric_question:
            return answer
        
        # Pattern 1: "3.5/4.0" or "3.5 / 4.0" → "3.5"
        # Pattern 2: "85/100" → "85"
        slash_pattern = r'^([\d.]+)\s*/\s*[\d.]+'
        match = re.match(slash_pattern, answer)
        if match:
            cleaned = match.group(1)
            self.logger.info(f"🧹 Cleaned: '{answer}' → '{cleaned}'")
            return cleaned
        
        # Pattern 3: "3.5 out of 4.0" → "3.5"
        out_of_pattern = r'^([\d.]+)\s*out\s*of\s*[\d.]+'
        match = re.match(out_of_pattern, answer, re.IGNORECASE)
        if match:
            cleaned = match.group(1)
            self.logger.info(f"🧹 Cleaned: '{answer}' → '{cleaned}'")
            return cleaned
        
        # Pattern 4: "85%" → "85"
        if '%' in answer:
            cleaned = answer.replace('%', '').strip()
            self.logger.info(f"🧹 Cleaned: '{answer}' → '{cleaned}'")
            return cleaned
        
        # Pattern 5: "$120,000" or "120000 USD" → "120000"
        if 'salary' in question_lower or 'compensation' in question_lower:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', answer)
            if cleaned:
                self.logger.info(f"🧹 Cleaned: '{answer}' → '{cleaned}'")
                return cleaned
        
        # Pattern 6: "5 years" → "5"
        if 'year' in question_lower:
            match = re.match(r'^([\d.]+)', answer)
            if match:
                cleaned = match.group(1)
                if cleaned != answer:
                    self.logger.info(f"🧹 Cleaned: '{answer}' → '{cleaned}'")
                return cleaned
        
        # If no pattern matched, return original
        return answer

    def is_match_likely(self, job_description):
        """
        Optional: Check if the job is a good match before applying.
        """
        prompt = f"""
        Analyze this job description against my resume.
        
        Resume: {self.resume_text}
        
        Job: {job_description[:2000]}
        
        Is this a reasonable match for my skills? Reply with only 'YES' or 'NO'.
        """
        # ... implementation similar to above ...
        pass
