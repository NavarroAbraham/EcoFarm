from __future__ import annotations

from core.adapters.mappers import map_certificate_model_to_entity
from core.application.errors import NotFoundError
from core.application.ports import CertificateRepositoryPort
from core.domain.entities import Certificate
from core.models import Certificate as CertificateModel


class DjangoCertificateRepository(CertificateRepositoryPort):
    def create_certificate(self, certificate: Certificate) -> Certificate:
        certificate_model = CertificateModel(
            order_id=certificate.order_id,
            user_id=certificate.user_id,
            course_name=certificate.course_name,
            certificate_number=certificate.certificate_number or '',
            external_certificate_id=certificate.external_certificate_id or '',
            external_download_url=certificate.download_url or '',
            issued_date=certificate.issued_date,
        )
        certificate_model.save()
        return map_certificate_model_to_entity(certificate_model)

    def get_certificate(self, certificate_id: int) -> Certificate:
        try:
            certificate_model = CertificateModel.objects.select_related('order').get(pk=certificate_id)
        except CertificateModel.DoesNotExist as exc:
            raise NotFoundError(f"Certificado {certificate_id} no encontrado") from exc
        return map_certificate_model_to_entity(certificate_model)

    def list_certificates_for_user(self, user_id: int) -> list[Certificate]:
        certificates = CertificateModel.objects.filter(user_id=user_id).select_related('order').order_by('-created_at')
        return [map_certificate_model_to_entity(cert) for cert in certificates]

    def get_certificate_by_order(self, order_id: int) -> Certificate | None:
        certificate = (
            CertificateModel.objects.filter(order_id=order_id)
            .select_related('order')
            .order_by('-created_at')
            .first()
        )
        if not certificate:
            return None
        return map_certificate_model_to_entity(certificate)
