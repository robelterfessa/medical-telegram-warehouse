select
    *
from dbt_medical_dbt_medical.fct_messages
where full_date > current_date
