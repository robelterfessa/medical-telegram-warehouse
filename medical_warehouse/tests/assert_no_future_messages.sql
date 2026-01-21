select
    f.*
from dbt_medical_dbt_medical.fct_messages f
join dbt_medical_dbt_medical.dim_dates d
  on f.date_key = d.date_key
where d.full_date > current_date
