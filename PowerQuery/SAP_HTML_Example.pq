let
    // =========================
    // PARÁMETROS (EDITABLES)
    // =========================
    SiteUrl              = "https://XXX.sharepoint.com/sites/NombreDelSitio/",
    CarpetaFiltro        = "Documentos compartidos/ReportesSAP/",     // "" si no querés filtrar por carpeta
    NombreArchivoHtml    = "ReporteSAP.html",
    RangoTablas          = {2..25},

    // =========================
    // CONEXIÓN A SHAREPOINT
    // =========================
    ArchivosSharePoint = SharePoint.Files(SiteUrl, [ApiVersion = 15]),
    FiltradoPorCarpeta = if Text.Length(CarpetaFiltro) > 0
                          then Table.SelectRows(ArchivosSharePoint, each Text.StartsWith([Folder Path], SiteUrl & CarpetaFiltro))
                          else ArchivosSharePoint,
    CoincidenciasArchivo = Table.SelectRows(FiltradoPorCarpeta, each [Name] = NombreArchivoHtml),
    _ValidarExistencia = if Table.RowCount(CoincidenciasArchivo) = 0
                         then error "No se encontró el archivo HTML en la ubicación indicada. Verificá 'CarpetaFiltro' y 'NombreArchivoHtml'."
                         else null,
    ArchivoHtml = CoincidenciasArchivo{0}[Content],
    HtmlComoTexto = Text.FromBinary(ArchivoHtml, TextEncoding.Utf8),

    // =========================
    // EXTRACCIÓN DESDE HTML
    // =========================
    TablasExtraidas = List.Transform(
        RangoTablas,
        (n) =>
            Html.Table(
                HtmlComoTexto,
                {
                    // ⚠ Ajustá nombres y posiciones según tu HTML
                    {"ReqmtsDate",          "td:nth-of-type(1)"},
                    {"Reserv.no.",          "td:nth-of-type(2)"},
                    {"Itm",                 "td:nth-of-type(3)"},
                    {"Material",            "td:nth-of-type(4)"},
                    {"Material Description","td:nth-of-type(5)"},
                    {"Reqmnt qty",          "td:nth-of-type(6)"},
                    {"Diff. qty",           "td:nth-of-type(7)"},
                    {"RemovedQty",          "td:nth-of-type(8)"},
                    {"BUn",                 "td:nth-of-type(9)"},
                    {"Plnt",                "td:nth-of-type(10)"},
                    {"SLoc",                "td:nth-of-type(11)"},
                    {"WBS Element",         "td:nth-of-type(12)"},
                    {"Recipient",           "td:nth-of-type(13)"},
                    {"S",                   "td:nth-of-type(14)"},
                    {"User",                "td:nth-of-type(15)"},
                    {"Order",               "td:nth-of-type(16)"}
                },
                [ RowSelector = "table:nth-of-type(" & Number.ToText(n) & ") tr" ]
            )
    ),
    TablasCombinadas = Table.Combine(TablasExtraidas),
    FilasLimpias = Table.SelectRows(TablasCombinadas, each [ReqmtsDate] <> "ReqmtsDate"),
    Tipado =
        Table.TransformColumnTypes(
            FilasLimpias,
            {
                {"ReqmtsDate", type text},          // cambiar a date si tu HTML trae fechas en formato estable
                {"Reserv.no.", type text},
                {"Itm", Int64.Type},
                {"Material", type text},
                {"Material Description", type text},
                {"Reqmnt qty", type number},
                {"Diff. qty", type number},
                {"RemovedQty", type number},
                {"BUn", type text},
                {"Plnt", type text},
                {"SLoc", type text},
                {"WBS Element", type text},
                {"Recipient", type text},
                {"S", type text},
                               {"User", type text},
                {"Order", type text}
            }
        )
in
  Tipado
