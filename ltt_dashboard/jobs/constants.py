FULL_TIME = 'full_time'
PART_TIME = 'part_time'
INTERNSHIP = 'internship'

JOB_TYPE_CHOICES = {
    (FULL_TIME, "Full Time"),
    (PART_TIME, "Part Time"),
    (INTERNSHIP, "Internship"),
}

NEW_APPLICANT = 'new_applicant'
IN_PROCESS = 'in_process'
RESERVED = 'reserved'
SELECTED = 'selected'
REJECTED = 'rejected'

APPLICATION_STAGE_CHOICES = {
    (NEW_APPLICANT, "New Application"),
    (IN_PROCESS, "In Process"),
    (RESERVED, "Reserved"),
    (SELECTED, "Selected"),
    (REJECTED, "Rejected"),
}
