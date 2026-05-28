import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.infra.repositories.customer_repository import CustomerRepository
from app.shared.exceptions import CustomerNotFoundException, ExternalIntegrationException, CepNotFoundException


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.db = db

    def _fetch_and_format_address(self, cep: str, numero: str = None, complemento: str = None) -> str:
        # Limpar o CEP para ter apenas números
        cep = "".join(filter(str.isdigit, cep))
        if len(cep) != 8:
            raise ExternalIntegrationException("Invalid CEP format")
            
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise ExternalIntegrationException("Failed to contact ViaCEP API")
            
        data = response.json()
        if data.get("erro"):
            raise CepNotFoundException()
            
        # Formatar endereço no padrão: Logradouro, Número - Complemento - Bairro, Cidade - UF
        endereco = f"{data.get('logradouro')}"
        if numero:
            endereco += f", {numero}"
        if complemento:
            endereco += f" - {complemento}"
        
        endereco += f" - {data.get('bairro')}, {data.get('localidade')} - {data.get('uf')}"
        return endereco

    def _process_address_kwargs(self, kwargs: dict, is_update: bool = False) -> dict:
        cep = kwargs.pop("cep", None)
        numero = kwargs.pop("numero", None)
        complemento = kwargs.pop("complemento", None)
        
        if cep:
            kwargs["endereco"] = self._fetch_and_format_address(cep, numero, complemento)
        elif not is_update and not kwargs.get("endereco"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'endereco' or 'cep' must be provided"
            )
        return kwargs

    def create_customer(self, **kwargs):
        kwargs = self._process_address_kwargs(kwargs, is_update=False)
        return self.repo.create(**kwargs)

    def get_customer(self, customer_id: str):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException()
        return customer

    def update_customer(self, customer_id: str, **kwargs):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException()
            
        kwargs = self._process_address_kwargs(kwargs, is_update=True)
        return self.repo.update(customer_id, **kwargs)

    def delete_customer(self, customer_id: str):
        success = self.repo.delete(customer_id)
        if not success:
            raise CustomerNotFoundException()
        return True

    def list_customers(self, nome: str = None, cpf: str = None, email: str = None, telefone: str = None):
        return self.repo.list_all(nome=nome, cpf=cpf, email=email, telefone=telefone)
