class Kurz(db.Model):
    __tablename__ = "Kurzy"

    ID_kurzu = db.Column(db.Integer, primary_key=True)
    Nazov_kurzu = db.Column(db.String, nullable=False)
    Typ_sportu = db.Column(db.String)
    Max_pocet_ucastnikov = db.Column(db.Integer)
    ID_trenera = db.Column(db.Integer, db.ForeignKey('Treneri.ID_trenera'))

    def __repr__(self):
        return f"<Kurz {self.Nazov_kurzu}>"